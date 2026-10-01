# my-final-assignment

A research assistant that answers developer questions from six corpus documents with checked citations, and refuses visibly when the sources say nothing.

![check](https://github.com/Abduovv/my-final-assignment/actions/workflows/check.yml/badge.svg)

## The problem

Developers ask questions against a small set of trusted documents and get fluent
answers with no idea what was actually used. Today a confident answer with a
wrong or missing citation looks identical to a grounded one, so readers cannot
tell support from invention.

## Demo

Two runs, pasted exactly as the commands printed them. Never an edited one.
`trace` prints every step the agent took, then the answer.

### One supported answer

```bash
uv run bootcamp capstone trace "How does chunking work in RAG?"
```

```text
[retrieve] top_k=3 -> [('rag-basics', 1), ('rag-basics', 2), ('evaluation-basics', 0)]
[llm_call] attempt 1: 121 chars
[decision] answered with citations []

answer: I do not know based on the provided corpus.
citations: []
confidence: 0.0
needs_human_review: True
```

On the offline FakeLLM this supported question still refuses: the fake cannot
read passages, so `citation_recall` and `claim_support` fail and the refusal is
the honest output. With a real model the same trace answers with `rag-basics`.

### One refusal

```bash
uv run bootcamp capstone trace "What is the capital city of Mongolia?"
```

```text
[retrieve] top_k=3 -> []
[decision] no relevant chunks; refusing without an LLM call

answer: I don't know based on the provided corpus.
citations: []
confidence: 0.0
needs_human_review: True
```

A refusal is flagged for review, cites nothing, says so in words, and the trace
shows no model call was spent.

## Architecture

One run is a chain: retrieve top_k=3 chunks by shared words, one model call with
a strict ResearchAnswer parser plus one corrective retry, citation verification
against what retrieval returned, then answer or flagged refusal. Provider errors
and timeouts become flagged refusals under `timeout_s` (30.0). One supported
question costs 1 model call; a refusal costs 0.

See [docs/adr/0001-run-shape.md](docs/adr/0001-run-shape.md).

## Measured results

Every number here comes from a command in this table, run on this commit. Say
which model produced it: CI has no keys, so a CI number is always the offline
fake model's.

| What | Command | Model | Result |
|---|---|---|---|
| Contract tests | `uv run pytest` | fake | `7 passed, 1 skipped, 1 xfailed` |
| Practice grader | `uv run bootcamp capstone grade` | fake | `score: 3/10 (30%) — NOT YET, critical safety gate failed` |
| Evaluation, before and after | see [docs/EVAL_REPORT.md](docs/EVAL_REPORT.md) | fake | before `3/10`, after `3/10` with provider/timeout hardening proven by pytest |

## The honest limitation

Rank 1 of docs/ISSUES.md used to be provider errors escaping as exceptions; it is
fixed, so the live limitation is rank 2: on the FakeLLM every grounded answer
fails because no model reads the passages, and the next step is putting a real
model in `.env` and re-running grade.

The full ranked list is in [docs/ISSUES.md](docs/ISSUES.md).

## How to run it

```bash
git clone https://github.com/Abduovv/my-final-assignment && cd my-final-assignment && uv sync && uv run pytest
```

No key needed: without a `.env` it runs on the offline fake model. For a real
model, copy `.env.example` to `.env`, fill in your provider, and
`uv sync --extra anthropic` (or `--extra openai`).

To hand in the final assignment, commit and push, then run
`uv run bootcamp capstone submit --github Abduovv`. It runs the practice set
first, then answers the final questions and opens the pull request.
`--dry-run` shows the bundle without handing anything in.

## Sources

No outside data beyond the six documents in data/corpus/. Session 13 applied:
any future outside source would be named here with its URL and retrieval date.

## Credits

Course pipeline from Gecko-Academy/dev3pack-cohort-2026-09 (`src/bootcamp_agent/`,
pinned at commit `85ad371e3e6354fc18edb4522b1fd66ac6223f62`); session notebooks
ch11 (state cap + per-user store) and ch14 (smoke + rollback sentence) shaped
`docs/RETENTION.md` and the rollback below.

## Rollback

Redeploy version 12 in 5 minutes via rollback to previous release.

---

| Path | What it is |
|---|---|
| `agent.py` | The agent: `YourAgent`, the class the tests, `trace` and the grader run |
| `tests/test_contract.py` | The capstone contract, as tests (`uv run pytest -k refusal`, `-k injection`, ...) |
| `data/corpus/` | The six source documents, versioned; nothing here writes to them |
| `docs/EVAL_REPORT.md` | Numbers you produced, before and after, with the command behind each |
| `docs/SKILL.md` | A skill another assistant can load (session 10) |
| `docs/adr/0001-run-shape.md` | The architecture decision and what would reverse it (session 10) |
| `docs/RETENTION.md` | What a session remembers, and what it refuses to (session 11) |
| `docs/ISSUES.md` | The ranked issue list (session 9, kept until 14) |

Built during the Dev3Pack AI Engineering bootcamp, on the course package at
commit `85ad371e3e6354fc18edb4522b1fd66ac6223f62` of https://github.com/Gecko-Academy/dev3pack-cohort-2026-09.
