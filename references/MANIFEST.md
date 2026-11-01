# Reference Source Manifest

Third-party repositories used for research only. **Read-only**: not modified, not installed, not imported by our code.
Cloned 2026-10-30 with `git clone --depth 1 --filter=blob:limit=2m --no-recurse-submodules` and `GIT_LFS_SKIP_SMUDGE=1`
(no model weights, no LFS assets, no submodules, blobs > 2 MB omitted). The trees are gitignored; re-create them from this table.

| Category | Repo | Branch | Commit SHA | Commit date | License | Size (no .git) | Files / .py |
|---|---|---|---|---|---|---|---|
| harness | [allenai/vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness) | main | `0cd7deb706982f25701fbd2c9ed45554f0cf46d7` | 2026-10-28 | Apache-2.0 | 8.4M | 799 / 164 |
| harness | [robocurve/inspect-robots](https://github.com/robocurve/inspect-robots) | main | `c8a821ba7bd44c042c95ab8f6a83d1e776cfb4a3` | 2026-10-28 | MIT | 6.8M | 408 / 171 |
| harness | [RLinf/RPent](https://github.com/RLinf/RPent) | main | `0e406bb96d670d0c18a4cea9a6ea047119661d19` | 2026-10-30 | Apache-2.0 | 5.7M | 495 / 331 |
| harness | [XPolicyLab/XPolicyLab](https://github.com/XPolicyLab/XPolicyLab) | main | `128e626278ef753fa8a86b16e3425a6359388b4c` | 2026-10-30 | Apache-2.0 | 218M | 9506 / 6511 |
| simulation | [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco) | main | `a650501666a708920d4e2eec7cf43e7c5925203e` | 2026-10-29 | Apache-2.0 | 121M | 2395 / 278 |
| benchmarks | [mani-skill/ManiSkill](https://github.com/mani-skill/ManiSkill) | main | `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3` | 2026-08-01 | Apache-2.0 | 376M | 1490 / 416 |
| benchmarks | [Lifelong-Robot-Learning/LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO) | master | `8f1084e3132a39270c3a13ebe37270a43ece2a01` | 2025-03-15 | MIT | 427M | 1116 / 99 |
| benchmarks | [robocasa/robocasa](https://github.com/robocasa/robocasa) | main | `dc73a8ce18e4b8947e8df2ae2958245ca823f3b4` | 2026-10-28 | MIT | 51M | 1243 / 876 |
| policies | [huggingface/lerobot](https://github.com/huggingface/lerobot) | main | `38b975c5bca0db0ce11a65705419cca001c6dafa` | 2026-10-29 | Apache-2.0 | 23M | 1304 / 1016 |
| policies | [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | main | `215abfb217dbac7d5f1273282331b9b1866c0479` | 2026-08-24 | Apache-2.0 | 2.0M | 142 / 91 |
| reasoning | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | main | `6f2df053f4487ce6ea8decc0d7482c8e46e0f132` | 2026-10-29 | MIT | 16M | 700 / 481 |
| reasoning | [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | main | `25162c4fc05c2d2d019b0ffb5b6b2a9f315ec007` | 2026-10-29 | MIT | 28M | 754 / 443 |
| evolution | [air-embodied-brain/Zetta-Embodiment](https://github.com/air-embodied-brain/Zetta-Embodiment) | main | `d7fd15ee63a5a1e7d546c5fc5b52db3b38331bc8` | 2026-10-27 | Apache-2.0 | 9.7M | 585 / 483 |
| evolution | [microsoft/agent-lightning](https://github.com/microsoft/agent-lightning) | main | `05c7fe133175653e48c990546a3509e52dc56512` | 2026-10-20 | MIT | 3.7M | 225 / 105 |

Notes
- ManiSkill, LIBERO and RoboCasa are both simulators and benchmarks; they are filed under `benchmarks/` because we consume them primarily as task suites.
- License column is from the top-level LICENSE file only. Sub-directory licenses, bundled assets and third-party model licenses are reviewed in `research/comparisons/license-matrix.md`.
- Memory-related repositories discovered during research are appended below after authenticity/license/maturity checks.

## Memory candidates (discovered)

Cloned 2026-10-30 with the same command as above into `references/memory/<repo>`. Static analysis only; see `research/projects/memory-landscape.md` for the candidate table and source analysis.

| Category | Repo | Branch | Commit SHA | Commit date | License | Size (no .git) | Files / .py |
|---|---|---|---|---|---|---|---|
| memory (episodic) | [NVIDIA-AI-IOT/remembr](https://github.com/NVIDIA-AI-IOT/remembr) | main | `964faab296fe70f8a8dbb9135adf20fecb758525` | 2025-03-02 | NVIDIA License (non-commercial: research/evaluation only) | 612K | 69 / 32 |
| memory (spatial) | [concept-graphs/concept-graphs](https://github.com/concept-graphs/concept-graphs) | main | `93277a02bd89171f8121e84203121cf7af9ebb5d` | 2025-01-15 | MIT | 2.4M | 70 / 42 |
| memory (spatial) | [MIT-SPARK/Spark-DSG](https://github.com/MIT-SPARK/Spark-DSG) | main | `3c40997e4ae739c56ed3cdd6ef5e882d403d8b64` | 2026-04-11 | BSD-2-Clause (LICENSE file; pyproject/PyPI say BSD-3-Clause) | 2.2M | 168 / 19 |
| memory (skill) | [NVlabs/ASPIRE](https://github.com/NVlabs/ASPIRE) | main | `fa00f0ef2bc1d91d594b9aa502c22133c9f538f7` | 2026-10-15 | Apache-2.0 | 33M | 341 / 205 |
| memory (general infra) | [mem0ai/mem0](https://github.com/mem0ai/mem0) | main | `26cdefb46600c0fa5953c4b5ee5003c125539fc4` | 2026-10-26 | Apache-2.0 | 42M | 1832 / 421 |
| memory (general infra) | [getzep/graphiti](https://github.com/getzep/graphiti) | main | `72b5c59c06607e09ea855be61b6ff5a3446fc951` | 2026-10-28 | Apache-2.0 | 24M | 424 / 302 |

Memory notes
- ReMEmbR's NVIDIA License (LICENSE.md §3.3) restricts use to non-commercial research/evaluation; treat it as design reference only and do not copy code.
- ASPIRE's `third_party/` submodules (LIBERO-PRO, robosuite, BEHAVIOR-1K, curobo, sam3, contact_graspnet_pytorch) were not fetched (`--no-recurse-submodules`).
- ConceptGraphs `main` is the batch pipeline; the README points to the `ali-dev` branch for the streaming refactor (not cloned).

## RSI frameworks (2026-10-30, second study)

Cloned with the same command into `references/evolution/<repo>`; reports in `research/projects/rsi-*.md`.
Some RoboMonkey / V-GPS / DSRL code lives in git submodules that were not fetched; the reports cite those files at the commits the parents pin.

| Category | Repo | Branch | Commit SHA | Commit date | License | Size (no .git) | Files / .py |
|---|---|---|---|---|---|---|---|
| evolution (self-modifying agent) | [jennyzzt/dgm](https://github.com/jennyzzt/dgm) | main | `a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2` | 2025-08-13 | Apache-2.0 | 55M | 1650 / 39 |
| evolution (self-modifying agent) | [MaximeRobeyns/self_improving_coding_agent](https://github.com/MaximeRobeyns/self_improving_coding_agent) | master | `ed8275dca4d3c5dbf77229964351fe9b424797dc` | 2025-04-24 | MIT | 2.2M | 141 / 110 |
| evolution (program search) | [algorithmicsuperintelligence/openevolve](https://github.com/algorithmicsuperintelligence/openevolve) | main | `bffd8c0ad858f6949e0cfd43edf8a7fbf45d0590` | 2026-10-30 | Apache-2.0 | 9.7M | 569 / 306 |
| evolution (program search) | [SakanaAI/ShinkaEvolve](https://github.com/SakanaAI/ShinkaEvolve) | main | `8adc053a2ce4511ad2ac310e004c530a73fb974a` | 2026-10-05 | Apache-2.0 | 14M | 326 / 222 |
| evolution (prompt/agent opt.) | [gepa-ai/gepa](https://github.com/gepa-ai/gepa) | main | `02ea4152ff6e512484cb5298046bfe967aea4735` | 2026-10-30 | MIT | 46M | 617 / 236 |
| evolution (prompt/agent opt.) | [ShengranHu/ADAS](https://github.com/ShengranHu/ADAS) | main | `2702bee8fefda42255efc5be9f60e3bd3db96ae4` | 2025-01-27 | Apache-2.0 | 26M | 863 / 30 |
| evolution (embodied skills) | [MineDojo/Voyager](https://github.com/MineDojo/Voyager) | main | `55e45a880755d0c8c66ca7fb5fe7962ac8974f89` | 2023-07-27 | MIT | 6.5M | 457 / 19 |
| evolution (reward evolution) | [eureka-research/Eureka](https://github.com/eureka-research/Eureka) | main | `9eee42808b52d8abc14845d1547bfde886403ccc` | 2024-05-03 | MIT (vendored isaacgymenvs BSD-3; Isaac Gym proprietary) | 354M | 1889 / 269 |
| evolution (reward evolution) | [eureka-research/DrEureka](https://github.com/eureka-research/DrEureka) | main | `1d4e00700423170717654516f4ef4b24cb0f3a84` | 2024-08-26 | MIT (legged_gym / rsl_rl BSD-3) | 101M | 316 / 179 |
| evolution (VLA steering) | [robomonkey-vla/RoboMonkey](https://github.com/robomonkey-vla/RoboMonkey) | main | `db9f8d314ea78e986f515617ac43afc58f984a53` | 2026-04-09 | MIT (verifier weights derive from Llama-2/Vicuna) | 2.4M | 143 / 69 |
| evolution (VLA steering) | [nakamotoo/V-GPS](https://github.com/nakamotoo/V-GPS) | main | `912a290f95a9f5fcf5942fbb5b9e7b4e99905c7b` | 2025-04-28 | **No LICENSE file (design only)** | 432K | 49 / 39 |
| evolution (VLA steering) | [nakamotoo/dsrl_pi0](https://github.com/nakamotoo/dsrl_pi0) | main | `7f48937d4553e95244cd81c79236a3256df80597` | 2026-04-26 | MIT | 348K | 57 / 47 |
| evolution (VLA steering) | [ajwagen/dsrl](https://github.com/ajwagen/dsrl) | main | `8d21b9cf55459f022c0e769bca1343edd9d30e5a` | 2025-08-05 | **No LICENSE file (design only)** | 6.2M | 16 / 3 |
| evolution (failure monitor) | [vla-safe/SAFE](https://github.com/vla-safe/SAFE) | main | `b8e31dfe4ea27d238f8f7b92f0c0f998a7179f78` | 2026-10-29 | MIT | 1000K | 73 / 43 |
| evolution (failure monitor) | [CXU-TRI/FAIL-Detect](https://github.com/CXU-TRI/FAIL-Detect) | main | `b758e55f7c0c988188f2e4876ffc03ae8a3c30ed` | 2025-06-18 | **CC-BY-NC-4.0 (design only)** | 19M | 400 / 253 |
| evolution (VLA RL) | [RLinf/RLinf](https://github.com/RLinf/RLinf) | main | `d80cf00e95e545f579e33432e7d7f14e86bb39d7` | 2026-10-30 | Apache-2.0 | 25M | 2234 / 968 |
| evolution (VLA RL) | [PRIME-RL/SimpleVLA-RL](https://github.com/PRIME-RL/SimpleVLA-RL) | main | `7c51662df27b586f9e8a1ab35fcf849f2b8852f9` | 2026-01-06 | MIT | 20M | 264 / 230 |

Surveyed, not cloned: FIPER (MIT), VLA-RL (Apache-2.0), RIPT-VLA (no license), FOREWARN (no code), pi*0.6/RECAP (paper only), AlphaEvolve (paper only).
