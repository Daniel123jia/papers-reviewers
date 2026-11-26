# P0: Review quality benchmark (draft)

This is an evaluator-only reference, not an input to the review engine. Do not inject this file or reference reviews into generation. Use fresh independent conversations for each run.

## TextCNN development case

Yoon Kim, *Convolutional Neural Networks for Sentence Classification*, EMNLP 2014, ACL Anthology D14-1181. Public source: https://aclanthology.org/D14-1181/ . Download the paper separately; no PDF or private review is distributed. The following targets are derived from the prior human/AI iterative review discussion and are not the exact original first-pass report. Recheck against the paper before scoring.

| ID | Target discovery / negative control | Evidence to verify |
|---|---|---|
| T01 | Pretrained initialization is the strongest empirical result; non-static beats rand on all seven tasks | Table 2 |
| T02 | Frozen branch does not explicitly constrain trainable embedding drift; distinguish independent and shared convolution weights, no assertion about code | §2, §4.1 |
| T03 | Static vs non-static changes known-word and randomly initialized OOV updates together; propose 2×2 control | §3.3 |
| T04 | Separate CNN, multiscale and parameter-count effects; avoid attributing performance solely to architecture | §3.1, §4.3 |
| T05 | SST-2 tuning / MR overlap is a potential question, not confirmed leakage | §3, §3.1 |
| T06 | Recompute model differences; single-channel convolution parameters 360300, independent two-channel 720300 with shared bias | Table 2, §3.1 |
| T07 | Dropout keep/drop probability conflict; p=.5 prevents this notation issue from implying a numerical error | §2.1 |
| T08 | Reject false tanh/ReLU contradiction; tanh is example, experiment uses ReLU | §2, §3.1 |
| T09 | 4/7 claim matches table, including multichannel alone; don't allege cherry picking | Table 2 |
| T10 | Authors acknowledge mixed multichannel findings; distinguish mechanism not proved from concealment | §4.1 |
| T11 | Phrase training explicitly disclosed; verify split at sentence level if needed | footnote 4 |
| T12 | Severity and decision account for 2014 six-page venue; avoid demanding a modern comprehensive journal study | paper context |

## Protocol

- Compare fresh web single-pass vs API single-pass using the same PDF bytes and same visible prompt. The exact historic first-pass prompt is not available here; current review_core.md is a reconstructed baseline, not a hidden web prompt. Save prompt/paper hashes, model/config, run date, usage and completion status. Multi-round web V2.0 is a separate exploratory reference, not the single-pass baseline.
- Blind label reports, assess against actual paper using at least one domain expert; repeat runs if budget allows. Score valid novel findings as well as target coverage. Hold out papers not used in prompt tuning (e.g. one FSL paper, one detection paper, one theory paper).
- Rubric (100): technical correctness 20; core reasoning depth 15; mathematical reasoning 15; experiment/attribution 15; accurate evidence 10; important discoveries 10; false positive control 10; severity/report quality 5. Record score rationale and evidence, not keyword matches.
- Gate: fabricated original claims/data/citations, unverified leakage stated as fact, or incomplete output invalidate acceptance regardless of score. Uncertainty explicitly marked is not a failure. Proposed target: no hard failures, both human-scored and benchmark coverage comparable to matched web baseline. No scores are claimed yet.
- Record report ID, evaluator, paper hash, prompt hash, per-target supported/partial/missed/false-positive, evidence, novel findings, rubric scores and decision. Do not expose private manuscripts or review results in GitHub.
