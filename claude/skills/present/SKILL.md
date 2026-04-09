---
name: present
description: Generate an HTML slide deck that visually explains a markdown file describing code changes
---

Review the given markdown file. Then generate a single self-contained HTML file that presents these changes as a visual slide deck.

Requirements:
- Self-contained HTML with inline CSS and JS (no external dependencies)
- Keyboard navigation (arrow keys) between slides
- Clean, modern design with a dark code theme
- Slide progression indicator (e.g., "3 / 12")
- No ASCII diagram/tables! Always go with HTML + CSS

Slide structure:
1. **Title slide**: Branch name, summary of what changed in 1-2 sentences
2. **Overview slide**: Bullet list of files changed, grouped by category (new, modified, deleted)
3. **Architecture slide** (if applicable): Simple diagram showing how the changed components relate to each other
4. **Per-change slides**: For each logical change:
   - What changed and why (plain English, assume the reader is unfamiliar with the codebase)
   - Syntax-highlighted code snippets showing before/after or key new code
   - Call out non-obvious design decisions or trade-offs
5. **Summary slide**: Key takeaways, anything reviewers should pay attention to

Style guidelines:
- Use monospace font for code, sans-serif for text
- Color-code additions (green) and removals (red) in diffs
- Keep each slide focused — one concept per slide
- Max ~15 lines of code per snippet; truncate with comments if longer

PDF Export:
- Add a "Export to PDF" button in the first slide
- The PDF should be landscape
- Each slide should be a new page in the PDF
- Fix the print-color-adjust so the PDF has the correct background color
- Things don't scroll on PDF, you need to adapt it
