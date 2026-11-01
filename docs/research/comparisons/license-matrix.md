# License Matrix

> Not legal advice. Based on each repository's LICENSE file and §7 of the source reports; anything involving weights, assets or commercial use requires legal confirmation.
> Reuse modes: **Dep** = use as a dependency; **Port** = port/rewrite code (retain copyright and NOTICE); **Proto** = protocol compatibility only (own implementation); **Design** = borrow design only; **Run** = run as an external process/container, do not copy.

## 1. Code

| Project | Commit | Code License | Planned reuse mode | Obligations / restrictions |
|---|---|---|---|---|
| vla-evaluation-harness | `0cd7deb` | Apache-2.0 | Proto + Run (images, model servers) | Retain NOTICE; **prebuilt image contents carry their own licenses** (each Dockerfile clones third-party simulators); BEHAVIOR-1K has an explicit license gate |
| inspect-robots | `c8a821b` | MIT | Port (ActionSemantics, compat, Approver, errors, registry) | Retain MIT copyright notice; `examples/pi05` inlines openpi code, check separately |
| RPent | `0e406bb` | Apache-2.0 | Port (`@tool`, Toolkit scheduling, HTTP RPC) | Retain file headers; transitive dependencies (Claude Agent SDK/Codex terms of service, SAM3, curobo) are not covered |
| XPolicyLab (framework layer) | `128e626` | Apache-2.0 | Design (WS transport pattern) | **Only** the framework layer (`client_server/`, `utils/`, `model_template.py`) can be extracted separately |
| XPolicyLab (`policy/` subdirectories) | Same as above | **Mixed**: Apache / MIT / **MPL-2.0** (H_RDT) / **NC** (InternVLA_A1_5, LDA_1B, G05, GalaxeaVLA, FLUX weights) / custom (DINOv3) / **no license** (~20, including physicalRSI, Mem_0, in-tree copy of diffusion_policy) | **Vendoring forbidden**; individual policies must be checked item by item |
| Zetta-Embodiment | `d7fd15e` | Apache-2.0 | Design + Port (gating, critic DSL schema) | `THIRD_PARTY_NOTICES.md`: derived from RPent and RLinf (`9ad44393`); copying must retain both layers of attribution |
| agent-lightning | `05c7fe1` | MIT | Design | Microsoft trademark terms; `examples/llm-in-sandbox/vendor` check separately |
| MuJoCo | `a650501` | Apache-2.0 | Dep (PyPI wheel) | Example MJCF in `model/` usable; Menagerie robot models **live in a separate repo, each with its own license** |
| ManiSkill | `62ff3a5` | Apache-2.0 (code); PyTorch3D snippets BSD-3 | Dep (separate venv) | See asset table |
| LIBERO | `8f1084e` | MIT | Dep (separate venv) / Run (vla-eval image) | See asset table; BDDL and init states can be considered MIT |
| RoboCasa | `dc73a8c` | MIT | Dep (separate venv) | See asset table |
| LeRobot | `38b975c` | Apache-2.0 | Dep (optional adapter package); data-format compatible | Weights individually per model card |
| openpi | `215abfb` | Apache-2.0 | Proto (WS protocol) + Run | See weights table |
| LangGraph | `6f2df05` | MIT | Dep (optional adapter package) | Do not depend on LangGraph Platform/`langgraph-api` (license not verified) |
| DSPy | `25162c4` | MIT (vendored lm15 MIT) | Dep (offline worker only) | License of the external `gepa` package not verified; **do not load untrusted `.pkl`** (cloudpickle) |
| Spark-DSG | See MANIFEST | BSD-2 (LICENSE) / BSD-3 (pyproject) | Dep (production spatial backend candidate) | Inconsistency needs confirmation; both are permissive |
| ConceptGraphs | See MANIFEST | MIT | Design / Port (association/fusion rules) | — |
| ASPIRE | See MANIFEST | Apache-2.0 | Design (skill validation gate protocol) | — |
| mem0 | See MANIFEST | Apache-2.0 | Dep (optional episodic backend) | — |
| Graphiti | See MANIFEST | Apache-2.0 | Design / Dep (optional) | — |
| ReMEmbR | See MANIFEST | **NVIDIA License (non-commercial)** | **Design only** | Code must not be copied |

## 2. Model weights

| Weights | License status | Constraints for worldcurrent |
|---|---|---|
| π0 / π0-FAST / π0.5 (openpi, LeRobot port) | **Not explicitly declared**; PaliGemma derivative, very likely subject to the **Gemma Terms of Use** (the openpi repo includes `LICENSE_GEMMA.txt` but does not reference it); the "Apache 2.0" in LeRobot docs covers code only | Tag `weights_license="gemma-tou (derivative, unconfirmed)"`; **legal review before external hosted inference** (Gemma ToU treats a Hosted Service as Distribution) |
| GR00T | NVIDIA Open Model License | Per its terms |
| SAM3 (used by RPent) | Meta license | Per its terms |
| VLAs inside XPolicyLab | Each different, several NC | Register each individually |

**Design requirement**: `weights_license` is **required** metadata in the Policy registry; the EvalLog records the weights used and their license status.

## 3. Simulation assets and datasets

| Asset | Declaration | Risk | Handling |
|---|---|---|---|
| ManiSkill assets | **CC BY-NC 4.0** (README); inspire_hand **CC BY-NC-SA**; some robots Apache/BSD | No commercial use | Treat as NC by default, research only |
| ManiSkill downloadable datasets (YCB, PartNet-Mobility, ReplicaCAD, AI2THOR...) | Each per its upstream; no per-item declaration in the repo | PartNet-Mobility research terms | Do not mirror |
| LIBERO assets | No per-item license; includes TurboSquid (usually forbids redistribution), Google Scanned Objects (CC BY), HOPE | Redistribution risk | **Do not redistribute**; users obtain them themselves |
| LIBERO datasets | README says CC BY 4.0 | Attribution | Cite |
| RoboCasa assets (~10GB, Objaverse + LightWheel + Luma) | README blanket CC BY 4.0; Objaverse per-object inherits the Sketchfab author license (including NC/SA) | Uncertain | **Do not redistribute**; audit item by item before publication/commercial use |
| MuJoCo Menagerie | Separate LICENSE per model | Some not Apache | Register before use |

## 4. Rules (to be written into engineering guidelines)

1. Code under `references/` **never** enters our packages; ported code must note the source repo, commit and original license in the file header, and be registered in the repository's `THIRD_PARTY_NOTICES.md`.
2. Copying any code from XPolicyLab `policy/`, ReMEmbR, MemoryVLA or physicalRSI is forbidden.
3. Weights and assets do not enter our git repository or images; setup scripts download them in the user's environment under upstream terms.
4. Each run's manifest records: code version, external benchmark commits, weight identifiers and license status, asset hashes.
