# Campaign configuration

Fields for an improvement campaign. Follow [Campaigns](../user-guide/campaigns.md) for setup and execution.

Campaign keys:

| Key | Default | Meaning |
|---|---|---|
| `experiment` | required | the experiment config to improve, relative to the campaign file |
| `experiment_overrides` | `{}` | dotted-path overrides applied to it |
| `proposer` | `rule.steering` | the generator (`{type, params}`) |
| `diagnosis` | `{}` | options for sorting failures, for example `stall_steps`, `regrasp` |
| `protocol` | see below | the gate settings |
| `cycles` | 1 | maximum cycles |
| `stop_after_no_progress` | 2 | stop after this many consecutive cycles without a promotion |
| `budget_s` | none | wall-clock limit for the campaign, checked before each cycle |
| `approval` | `auto` | or `manual` |
| `out_dir` | `runs/evolve` | the campaign directory, relative to the working directory |

Gate settings (`protocol:`):

| Key | Default | Meaning |
|---|---|---|
| `alpha` | 0.05 | false-promotion rate per cycle, Holm-corrected across that cycle's candidates |
| `stage1_pairs` | 10 | pairs used for early rejection |
| `stage1_max_deficit` | 2 | reject in stage 1 when parent wins minus candidate wins is this or more |
| `gate_top_k` | 1 | candidates sent to the gate |
| `gate_looks` | 1 | sequential looks; the benchmark must provide `gate_r1`, ... |
| `spending_rho` | 3.0 | alpha spent by look k is `alpha * (k/K)^rho` |
| `futility_stop` | true | stop a candidate once it no longer leads the parent on the gate |
| `max_task_regression` | 0.15 | veto: success on any task may not drop by more than this |
| `max_safety_increase` | 1.0 | veto: mean safety interventions per episode may not rise by more than this |
| `max_candidates` | 8 | candidates evaluated per cycle |
| `budget_s` | none | wall-clock limit per cycle, checked before each candidate |
| `prescreen` | none | `{env: {type: world_model, params: {path}}, split, margin}`: reject candidates a world model predicts below parent minus margin |
| `gate_test` | `{type: mcnemar}` | the paired statistic (`gate_tests` plugin), for example `{type: sign, params: {metric: steps, direction: lower}}` |
