1. 现在这个benchmark主流程是运行 @scripts/run_eval.sh 执行，总体上很好，但是有1个问题：
   1. 如果连续遇到api限制（比如连续10个），最可能是遇到限流了。这时候建议先sleep 30min，再试；