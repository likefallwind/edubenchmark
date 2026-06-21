#!/usr/bin/env python3
"""Vision pre-flight probe for EduIllustrate judge candidates.

The EduIllustrate score is a geometric mean over 8 dimensions, 4 of which send
base64 images to the judge. A text-only judge therefore cannot produce a
comparable score, so we gate each gateway judge on whether it actually accepts
image input — confirmed text-only models are dropped (per user decision).

For each model, send one minimal ``[text + 1x1 PNG]`` chat request to the
OpenAI-compatible gateway and classify:
  * ``vision``    — HTTP 200 with non-empty content (model saw the image)
  * ``text_only`` — HTTP 4xx whose body mentions image/modality/multimodal/vision
  * ``error``     — any other failure (gateway down, timeout, unknown 5xx)

Writes a ``vision_probe.json`` summary and prints the kept (vision) model list.
Exit code is always 0; the runner reads the JSON to decide what to run.
"""
import argparse
import base64
import json
import os
import struct
import sys
import urllib.error
import urllib.request
import zlib


def _solid_png(size=32, rgb=(220, 40, 40)):
    """Build a solid-color PNG of (size x size) with stdlib only.

    Some vision backends reject images below ~14px (doubao), so the probe image
    must be comfortably larger than any such minimum.
    """
    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB
    row = b"\x00" + bytes(rgb) * size                          # filter byte + pixels
    raw = row * size
    sig = b"\x89PNG\r\n\x1a\n"
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


_PROBE_PNG = _solid_png(32)

TEXT_ONLY_MARKERS = (
    "image", "modality", "multimodal", "vision", "not support", "unsupported",
    "图片", "图像", "多模态", "不支持",
)


def probe(model, base_url, api_key, timeout):
    url = base_url.rstrip("/") + "/chat/completions"
    data_uri = "data:image/png;base64," + base64.b64encode(_PROBE_PNG).decode()
    body = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What color is this 1x1 image? One word."},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }],
        "max_tokens": 64,
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode())
        choices = payload.get("choices") or []
        content = (choices[0].get("message", {}).get("content") if choices else "") or ""
        if content.strip():
            return {"status": "vision", "detail": content.strip()[:80]}
        return {"status": "error", "detail": "empty content on 200"}
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode()[:400]
        except Exception:
            err_body = ""
        low = err_body.lower()
        if e.code in (400, 415, 422) and any(m in low for m in TEXT_ONLY_MARKERS):
            return {"status": "text_only", "detail": f"HTTP {e.code}: {err_body[:200]}"}
        return {"status": "error", "detail": f"HTTP {e.code}: {err_body[:200]}"}
    except Exception as e:  # timeout, conn refused, etc.
        return {"status": "error", "detail": f"{type(e).__name__}: {str(e)[:200]}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--base-url", default=os.environ.get("API_GATEWAY_BASE_URL", "http://127.0.0.1:8111/v1"))
    ap.add_argument("--api-key-env", default="API_GATEWAY")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--out", default="vision_probe.json")
    args = ap.parse_args()

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        print(f"ERROR: {args.api_key_env} not set", file=sys.stderr)
        sys.exit(2)

    results = {}
    kept = []
    for m in args.models:
        r = probe(m, args.base_url, api_key, args.timeout)
        results[m] = r
        flag = {"vision": "✅ vision", "text_only": "⛔ text-only (drop)", "error": "⚠️ error"}[r["status"]]
        print(f"  {m:24s} {flag}  {r['detail']}")
        if r["status"] == "vision":
            kept.append(m)

    out = {"base_url": args.base_url, "results": results, "kept": kept}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("KEPT:", ",".join(kept) if kept else "(none)")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
