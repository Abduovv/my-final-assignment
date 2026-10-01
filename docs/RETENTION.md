# Retention policy

**Filled by:** session 11. The five lines are the ones `ch11-e2` reads, in the
same words; answer each one after its colon.

STORED: one answer_style preference and the last 5 question summaries (episodes).

WHY: to personalize answers and keep recent context without unbounded growth.

CORRECTED BY: the user editing preferences or asking again; reset() clears both.

EXPIRES: episodes expire after 5 entries; preferences expire on reset or user change.

WE REFUSE TO REMEMBER: personal data, secrets, credentials, payment details, anything we cannot justify keeping.

## How the code enforces it

The capstone agent itself keeps no cross-question memory yet, so there is no
retention to enforce in `agent.py`. The placeholder contract test
`test_memory_is_capped_reset_and_kept_per_user` in tests/test_contract.py stays
`skip` until session 11 is wired; the reference implementation that proves the
cap (last 5 episodes), the reset, and per-user isolation lives in the ch11
notebook (`answer_with_state` plus `MemoryStore`).
