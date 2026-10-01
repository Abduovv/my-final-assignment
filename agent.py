"""Your capstone agent: the one your README demos and your CI grades.

It starts as the final assignment's starter, unchanged: the same `YourAgent`,
the same `answer_question` pipeline from the course package, the same budget.
Calling it returns a `bootcamp_agent.schema.ResearchAnswer`, the contract the
whole course used, so everything you built in the sessions plugs in here.
`run(question)` returns the whole `AgentResult`, trace included, which is what
`uv run bootcamp capstone trace "<question>"` prints.

As shipped it is honest and insufficient. On the offline `FakeLLM` it refuses
what it should refuse and answers nothing else, and some contract tests in
`tests/test_contract.py` are marked as expected failures on purpose. Making them
pass is the work. What to add, session by session, is in `docs/` (each file
names the session that fills it).

The provider comes from `.env` (`BOOTCAMP_PROVIDER`), and falls back to the
offline `FakeLLM`. Keys live only in `.env`, which git ignores.
"""

from __future__ import annotations

from pathlib import Path

from bootcamp_agent.agent import AgentResult, answer_question
from bootcamp_agent.config import load_settings
from bootcamp_agent.documents import Document, load_corpus
from bootcamp_agent.llm import LLMClient, get_client
from bootcamp_agent.schema import ResearchAnswer
from bootcamp_agent.tools import Tool, build_tools


def _flagged_refusal(text: str = "I don't know based on the provided corpus.") -> ResearchAnswer:
    """A refusal as a value: flagged, cited nothing, low confidence.

    Session 2 (ch02-e4) taught the shape; session 14 wires it into YourAgent so
    a provider error or timeout never escapes as an exception.
    """
    return ResearchAnswer(
        answer=text,
        citations=(),
        confidence=0.0,
        needs_human_review=True,
    )


#: The six course documents, copied in by `bootcamp capstone new`. Versioned
#: input: nothing you build writes to it.
CORPUS_DIR = Path(__file__).resolve().parent / "data" / "corpus"


class YourAgent:
    """The agent the tests and the grader run. Make it yours."""

    #: How long one provider call may take before the agent gives up with a
    #: flagged refusal. NOT ENFORCED YET: the starter waits for ever, which is
    #: why the `timeout` contract test is marked xfail. The test sets this low
    #: and expects an answer inside a second.
    timeout_s: float = 30.0

    def __init__(self, client: LLMClient | None = None) -> None:
        self.documents: list[Document] = load_corpus(CORPUS_DIR)
        self.client: LLMClient = client if client is not None else get_client(load_settings())
        # Every tool the agent can reach. Session 4's registry, read-only by
        # construction; session 12 has you classify each one, and the `tools`
        # contract test refuses anything not classified as a reader.
        self.tools: dict[str, Tool] = build_tools(self.documents, self.client)

    def run(self, question: str) -> AgentResult:
        """One question, answered or refused, with the trace of how.

        Hardening (sessions 2/14): the provider runs under ``timeout_s`` and any
        provider error becomes a flagged refusal, never a raised exception. The
        timeout uses a worker thread so a hanging provider cannot hang the run.
        """
        import concurrent.futures

        def _answer() -> AgentResult:
            return answer_question(
                question,
                self.documents,
                self.client,
                max_tool_calls=3,
                top_k=3,
            )

        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = pool.submit(_answer)
            try:
                return future.result(timeout=self.timeout_s)
            except Exception:
                from bootcamp_agent.agent import TraceEvent

                return AgentResult(
                    answer=_flagged_refusal(),
                    trace=(TraceEvent("decision", "provider error or timeout; flagged refusal"),),
                )
        finally:
            pool.shutdown(wait=False, cancel_futures=True)

    def __call__(self, question: str) -> ResearchAnswer:
        return self.run(question).answer
