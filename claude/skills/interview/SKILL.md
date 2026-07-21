---
name: interview
description: Interview the user about technical preferences before implementing a task
---

Interview me about how I want the code to look like for the following task:

$ARGUMENTS

I want to be very opinionated about everything technical, like naming, design pattern, architecture, trade-offs, and the whole technical implementation.
You can only ask me one question at a time. Keep in your context all the questions you want to make, but you can only ask me one at a time.

Lead every question with **your recommended answer and the reasoning behind it**, so I confirm or correct rather than answer from a blank page. Draw the recommendation from the codebase, my CLAUDE.md preferences, and sensible defaults. If you genuinely have no lean, say so and give me the trade-off instead.

Before asking ANY QUESTION, investigate the codebase. The code probably already answer most of your questions. Do not assume stuff. Verify if the existing code has what you need, or if you need to create it.
