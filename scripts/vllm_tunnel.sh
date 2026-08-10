#!/usr/bin/env bash
# 打开到自建 vLLM 服务器 (Qwen/Qwen3.5-4B) 的 SSH 隧道。
#
# 为什么需要隧道: vLLM 只在容器内的 8000 端口监听, 对外宣称的 115.190.90.101:63550
# 上没有任何进程 (实测 connection refused), 宿主机的公网 8000 又被另一个跑 sglang
# 视频模型的容器占着。等端口映射修好之后这个脚本就可以不用了 —— provider 的
# base_url 默认值本来就写的是公网地址。
#
#   ./scripts/vllm_tunnel.sh                 # 前台开隧道, Ctrl-C 关闭
#   ./scripts/vllm_tunnel.sh --check         # 只探活, 不开隧道
#   LOCAL_PORT=8811 ./scripts/vllm_tunnel.sh # 换本地端口
#
# 隧道开着的时候这样跑评测:
#   VLLM_BASE_URL=http://127.0.0.1:63550/v1 \
#     python3 scripts/eval_benchmark.py --benchmark <name> --model Qwen/Qwen3.5-4B
set -euo pipefail

SSH_HOST="${SSH_HOST:-root@115.190.90.101}"
SSH_PORT="${SSH_PORT:-23578}"
LOCAL_PORT="${LOCAL_PORT:-63550}"
REMOTE_PORT="${REMOTE_PORT:-8000}"   # vLLM 在容器内监听的端口

probe() {
    curl -s -m 10 "http://127.0.0.1:${LOCAL_PORT}/v1/models"
}

if [[ "${1:-}" == "--check" ]]; then
    echo "探测 127.0.0.1:${LOCAL_PORT} ..."
    probe || { echo "连不上 —— 隧道没开?"; exit 1; }
    echo
    exit 0
fi

echo "隧道: 127.0.0.1:${LOCAL_PORT} -> ${SSH_HOST} 容器内 127.0.0.1:${REMOTE_PORT}"
echo "另开一个终端验证: ./scripts/vllm_tunnel.sh --check"
echo "Ctrl-C 关闭。"
exec ssh -N \
    -p "${SSH_PORT}" \
    -o ExitOnForwardFailure=yes \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -L "${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT}" \
    "${SSH_HOST}"
