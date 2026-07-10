- Design for testability, with a preference for the "functional core, imperative shell" pattern
- Prefer simple designs
- Prefer designs that make use of well-known software design patterns
- Prefer tests with no/few mocks
- Prefer parametrized tests when possible
- Never use typeof for validation in TS/JS; use zod instead
- When working with external libraries or frameworks, use the context7 MCP to fetch up-to-date documentation rather than relying on training data
- Prefer targeted test runs (pytest path::name -q, npm run test:unit -- <file>) over running the full suite
- Avoid mixing levels of abstraction; prefer local helper functions or separate modules depending on the likelihood of reusability

## Collaboration style

- **Contract-first split for new functions I want to own:** I'll stub the function signature (owning the contract); you write the tests against that stub; I fill in the implementation to make the tests pass. When you see a stubbed function with no body and no tests, default to writing the tests rather than the implementation unless I say otherwise.
- **Be mindful of what I should own vs delegate.** Architecture decisions, error/retry/idempotency behavior, and anything I'll have to operate are worth me owning — flag when a change touches these so I can take the pen. Boilerplate, glue code, scaffolding, and mechanical refactors are fine to hand off without ceremony.
- **Work in small reviewable chunks with approval gates between them.** Default chunk size is one logical change with its tests (~1–3 files); don't artificially split a coherent edit. After each chunk, summarize what landed and stop — wait for "ok"/"next"/"proceed"/"looks good" or specific tweaks before continuing. "Proceed" on chunk 1 does not authorize chunk 2; re-confirm at each boundary. A pre-built task list is fine, it just doesn't authorize back-to-back execution.
