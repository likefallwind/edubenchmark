#!/usr/bin/env python3
"""并发效率压测：对自建 vLLM (Qwen/Qwen3.5-4B) 逐档测吞吐。

    python3 scripts/bench_vllm_concurrency.py 192 8,16,32,48,64,96,128

设计要点（改之前先读，这几条都是踩出来的）：

- **必须固定输出长度**（``max_tokens`` + ``ignore_eos``，vLLM 官方 benchmark_serving
  的做法），否则测的是"最长那道题多久跑完"而不是并发效率。第一版用变长输出测，16 路
  那档跑了 27 分钟，最后 7 分钟服务端只剩 1 个请求在跑，聚合吞吐被稀释到 882 tok/s——
  同样 16 路在固定长度口径下是 1796 tok/s，差一倍。
  这里设 ``max_tokens`` 不违反仓库的 no-max_tokens 政策：那条政策针对评测正确性，
  本脚本只测服务吞吐，不产出任何评测分数。
- 用 mmlu_pro 的真实 prompt 而非合成负载，prefill 规模贴近实际。
- 请求数取各并发档的公倍数（如 192 对应 16/32/48/64 的 12/6/4/3 个满批次），
  让尾部空转在各档位上同等。
- 流式读取，因此能分出 TTFT（反映排队）和整体延迟。判断吞吐平掉是"算力饱和"还是
  "撞 max-num-seqs"就靠 TTFT：前者平滑上升，后者阶跃跳变且服务端出现 Waiting>0。

2026-08-10 实测结论见 CLAUDE.md 的 vllm provider 段落：64 是性价比拐点。
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/home/likefallwind/code/edubenchmark/scripts")
from eval.benchmarks import get_adapter  # noqa: E402

BASE = "http://115.190.90.101:63550/v1/chat/completions"
MODEL = "Qwen/Qwen3.5-4B"


def build_prompts(n: int) -> list[list[dict]]:
    ad = get_adapter("mmlu_pro")
    items = ad.load_items(limit=n)
    return [ad.build_messages(it) for it in items]


FIXED_OUT = int(__import__("os").environ.get("FIXED_OUT", "512"))


def one_request(messages: list[dict]) -> dict:
    # 固定输出长度: max_tokens + ignore_eos 让每个请求恰好生成 FIXED_OUT 个 token。
    # 这样各并发档的总工作量严格相等、没有长尾, 吞吐可以直接相除比较。
    # (vLLM 官方 benchmark_serving 用的就是这个手法。仓库的 no-max_tokens 政策针对的是
    #  评测正确性, 这里是压测, 不产出任何评测分数。)
    body = json.dumps(
        {
            "model": MODEL,
            "messages": messages,
            "temperature": 0,
            "max_tokens": FIXED_OUT,
            "ignore_eos": True,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
    ).encode()
    req = urllib.request.Request(
        BASE, data=body, headers={"Content-Type": "application/json"}
    )
    t0 = time.perf_counter()
    ttft = None
    usage = {}
    try:
        with urllib.request.urlopen(req, timeout=1800) as resp:
            for raw in resp:
                if not raw.startswith(b"data: "):
                    continue
                payload = raw[6:].strip()
                if payload == b"[DONE]":
                    break
                chunk = json.loads(payload)
                if chunk.get("usage"):
                    usage = chunk["usage"]
                ch = chunk.get("choices") or []
                if ttft is None and ch:
                    d = ch[0].get("delta") or {}
                    if d.get("content") or d.get("reasoning") or d.get(
                        "reasoning_content"
                    ):
                        ttft = time.perf_counter() - t0
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": f"{type(exc).__name__}: {exc}"[:120]}
    total = time.perf_counter() - t0
    return {
        "ok": True,
        "latency": total,
        "ttft": ttft if ttft is not None else total,
        "completion_tokens": usage.get("completion_tokens", 0),
        "prompt_tokens": usage.get("prompt_tokens", 0),
    }


def run_level(conc: int, prompts: list[list[dict]]) -> dict:
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=conc) as ex:
        res = list(ex.map(one_request, prompts))
    wall = time.perf_counter() - t0
    ok = [r for r in res if r["ok"]]
    fail = [r for r in res if not r["ok"]]
    comp = sum(r["completion_tokens"] for r in ok)
    prom = sum(r["prompt_tokens"] for r in ok)
    lat = sorted(r["latency"] for r in ok)
    ttft = sorted(r["ttft"] for r in ok)
    q = lambda xs, p: xs[min(len(xs) - 1, int(len(xs) * p))]  # noqa: E731
    return {
        "concurrency": conc,
        "requests": len(prompts),
        "ok": len(ok),
        "failed": len(fail),
        "errors": [r["err"] for r in fail[:3]],
        "wall_s": round(wall, 1),
        "completion_tokens": comp,
        "prompt_tokens": prom,
        "output_tok_s": round(comp / wall, 1) if wall else 0,
        "total_tok_s": round((comp + prom) / wall, 1) if wall else 0,
        "req_per_min": round(len(ok) / wall * 60, 2) if wall else 0,
        "latency_p50": round(q(lat, 0.5), 1) if lat else None,
        "latency_p95": round(q(lat, 0.95), 1) if lat else None,
        "ttft_p50": round(q(ttft, 0.5), 2) if ttft else None,
        "ttft_p95": round(q(ttft, 0.95), 2) if ttft else None,
        "per_stream_tok_s": (
            round(statistics.mean(r["completion_tokens"] / r["latency"] for r in ok), 1)
            if ok
            else 0
        ),
    }


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 192
    levels = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [
        16,
        32,
        48,
        64,
    ]
    prompts = build_prompts(n)
    print(f"prompts={len(prompts)} levels={levels}", flush=True)
    out = []
    for c in levels:
        print(f"--- 并发 {c} 开始 ---", flush=True)
        r = run_level(c, prompts)
        out.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
        time.sleep(10)  # 让服务端队列排空，避免相互干扰
    print("=== ALL ===", flush=True)
    print(json.dumps(out, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
