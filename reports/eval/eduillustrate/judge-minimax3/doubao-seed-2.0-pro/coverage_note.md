# doubao-seed-2.0-pro 覆盖率说明（务必先读）

生成 230 题，**出稿 206 题，渲染失败 24 题（覆盖率 89.6%）**。

| 指标 | 值 | 含义 |
|---|---|---|
| `overall_mean_judged_only` | **3.7055** | 只算出稿的 206 题 |
| `overall_mean_all_items` | **3.3188** | 失败题计 0，按 230 分母 |

## ⚠️ 不要直接用 3.7055 跟别的模型比

3.7055 是四个模型里最高的 judged 分，但**有幸存者偏差**：失败的 24 题不是随机分布，而是模型"画不出来"的那批难题——它们被排除后，剩下的样本自然偏容易。

按全量 230 的公平口径（`overall_mean_all_items`）横向对比，doubao-pro 实际排第二：

| 模型 | 判卷 | 失败 | judged | **all-230** |
|---|---|---|---|---|
| kimi-k2.7-code | 229 | 1 | 3.590 | **3.574** |
| **doubao-seed-2.0-pro** | 206 | 24 | 3.705 | **3.319** |
| MiniMax-M3 | 230 | 0 | 3.175 | **3.175** |
| doubao-seed-2.0-lite | 180 | 50 | 3.389 | **2.652** |

偏差的证据：biology-g12 只判了 12/15，该科折算分 2.58（全场最低）；难度「难」的题失败 19/173。

## 失败原因：模型幻觉出不存在的 Manim API

24 题**全部**卡在 Scene 1（Scene 1 挂掉后，增量策略下 Scene 2+ 被阻断，整题无产出）。每题都用满了 3 轮自动修复（v0→v3），模型反复编造同类不存在的 API，没能自愈。

错误类型：TypeError ×13、NameError ×6、AttributeError ×3、ImportError/ModuleNotFoundError ×2。
**没有一例是 LaTeX / 环境问题**（与 xelatex、mhchem 等环境缺口无关），纯粹是模型写不对 Manim。

典型幻觉：`Color()`、`Helix`、`Hatch`、`manim.optics`、`Axes.grid`、`MobjectTable.merge_cells`，以及 `dash_pattern` / `stroke_style` / `center` / `buff` 这类不存在的构造参数。

<details>
<summary>24 题完整清单</summary>

| 题目 | 末次错误 |
|---|---|
| problem_18_physics_g9 | NameError: name 'Helix' is not defined |
| problem_26_biology_g12 | AttributeError: MobjectTable object has no attribute 'merge_cells' |
| problem_34_math_g6 | TypeError: Mobject.__init__() got an unexpected keyword argument 'dash_pattern' |
| problem_73_physics_g12 | TypeError: Mobject.__init__() got an unexpected keyword argument 'center' |
| problem_83_physics_g12 | NameError: name 'CENTER' is not defined |
| problem_86_physics_g12 | TypeError: Mobject.__getattr__.<locals>.setter() got an unexpected keyword |
| problem_87_physics_g12 | TypeError: Mobject.__getattr__.<locals>.setter() missing 1 required positional |
| problem_94_math_g9 | NameError: name 'CENTER' is not defined |
| problem_95_math_g9 | AttributeError: Axes object has no attribute 'grid' |
| problem_104_math_g9 | NameError: name 'Color' is not defined |
| problem_107_math_g9 | ImportError: cannot import name 'Color' from 'manim' |
| problem_115_geography_g9 | TypeError: Mobject.__getattr__.<locals>.getter() takes 1 positional argument |
| problem_119_physics_g9 | TypeError: Mobject.align_to() got an unexpected keyword argument |
| problem_125_physics_g9 | ModuleNotFoundError: No module named 'manim.optics' |
| problem_136_chemistry_g12 | TypeError: Mobject.__getattr__.<locals>.setter() got an unexpected keyword |
| problem_139_biology_g12 | TypeError: Mobject.__init__() got an unexpected keyword argument 'stroke_style' |
| problem_146_biology_g12 | TypeError: Mobject.__init__() got an unexpected keyword argument 'dash_pattern' |
| problem_148_chemistry_g9 | NameError: name 'Hatch' is not defined |
| problem_185_geography_g12 | TypeError: Mobject.__getattr__.<locals>.setter() got an unexpected keyword |
| problem_195_math_g12 | NameError: name 'get_intersections' is not defined |
| problem_196_math_g12 | TypeError: RightAngle.__init__() got multiple values for argument 'length' |
| problem_199_math_g12 | TypeError: Mobject.__getattr__.<locals>.getter() takes 1 positional argument |
| problem_201_physics_g12 | TypeError: Mobject.align_to() got an unexpected keyword argument 'buff' |
| problem_208_physics_g12 | AttributeError: 'list' object has no attribute 'rotate' |

</details>

## 运行参数

- 生成：`scripts/run_doubao_pro.sh`，全量 benchmark.json（230 题），provider = 本地 gateway，并发 topic=4 / scene=4，max_retries=3，耗时约 8.2h
- 评测：`scripts/eval_eduillustrate.sh output/doubao_pro doubao-seed-2.0-pro MiniMax-M3`，max_workers=4，retry_limit=2
- 同目录下另有 `reports/eval/eduillustrate/doubao-seed-2.0-pro/`（仅 4 题），那是 2026-06-21 的旧·部分跑，与本次全量无关。
