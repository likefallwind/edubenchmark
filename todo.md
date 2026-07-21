1. 筛选出一个精选题集；以后默认做精选题集，需要再做全量
   - [x] 方案 + 题单 + 离线验证 + MINI=1 开关，已合并 master（2026-07-21，merge 48632cc）；已用 MiniMax-M3 各 5 题 smoke 通过 26/26
   - [ ] 用真实模型整跑一版精选（`MINI=1 ./scripts/run_eval.sh`，须在 miniconda python 下），落到隔离树 `reports/eval_mini_v1/`，验证 --item-list sha256 入库与输出隔离在真实规模下也 OK
   - [ ] 聚合四步管线接入 mini：读 `reports/eval_mini_v1/` → 输出 `reports/atomic_ability_rebenchmark_mini_v1/`，每个 P 标记 mini 面（不与全量画像混淆）
2. 评测场，网站
3. 评测场，外部benchmark持续进入机制
4. 网页形式输出现在的结论
5. agent测试