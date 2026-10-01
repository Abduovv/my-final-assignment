# Ranked issues

**Filled by:** session 9 (the first list, `cap01-e5`), kept current until
session 14, which fixes rank 1 and adds its regression test.

At least three rows. Ranks 1, 2, 3... with no gap and no tie: two issues ranked
1 is a list nobody prioritised. The impact is what orders it.

The columns are the three fields `cap01-e5` reads.

| rank | issue | impact |
|---:|---|---|
| 1 | Provider errors escaped as exceptions instead of flagged refusals, crashing the run when the provider is down. | Any provider outage becomes a crash instead of an answer, so the caller handles two shapes and the grader records agent_completed failures. |
| 2 | On the offline FakeLLM, all seven grounded practice questions fail citation_recall and claim_support because the fake cannot read passages. | The practice score caps at 3/10 and the critical safety gate fails, so no offline run can approach the certificate bar. |
| 3 | An obeyed injected instruction that cites only retrieved documents can return ACCESS GRANTED unflagged with full confidence. | A document writer can dictate the answer while staying inside the citation check, which is the exact spend/grant class the course refuses to ship. |

## Rank 1, in progress

- The fix: `YourAgent.run` executes `answer_question` under `timeout_s` in a worker thread and converts any provider error or timeout into a flagged refusal (answer says it does not know, zero citations, confidence 0.0, needs_human_review true).
- The regression test: `test_regression_rank_1_of_the_issue_list` in tests/test_contract.py
- Before and after: see [EVAL_REPORT.md](EVAL_REPORT.md).
