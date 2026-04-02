# Technical Research Style Guide

## 1. Structural Hierarchy & Formatting

- **Paragraph Density:** Keep paragraphs tight and concise, strictly limited to 4-5 lines.
- **Lists:** Transition from prose to bulleted/numbered lists only when detailing process steps or highlighting secondary aspects that warrant visual separation.
- **Code Blocks:** Always wrap error messages, logs, terminal commands, and code snippets in standalone code blocks. Snippets should be tight—omit unnecessary symbolic density.
- **Typography:** Apply **bolding** for critical system warnings and key terms. Use *italics* based on the natural rhythm and "sound" of the phrasing.

## 2. Syntax & Punctuation

- **The Pause:** Use ellipses (...) to string together complex thoughts, providing a "digestive pause" before introducing a clarifying analogy or shifting focus.
- **Semicolons:** Employ semicolons to balance related, complex thoughts within a single sentence without breaking flow.
- **Jargon Integration:** Introduce industry jargon and acronyms fluently within narrative text. Define concepts naturally inline rather than relying on parenthetical definitions.

## 3. Tone & Persona

- **Perspective (The Detached Authority):** Write as a solo researcher. Strictly avoid first-person ("I") and collective ("we"). Use clever phrasing to describe actions as general observations or systemic results (e.g., "Resolution requires..." or "The audit revealed...").
- **Emotional Baseline:** Maintain pragmatic realism. Acknowledge skeptical points, remain detached, but avoid clinical sterility.
- **Humor:** Inject subtle, dry humor using domain-adjacent analogies or metaphorical irony. Use sparingly—lighten dense passages without distracting from the technical core.
- **Modality:** Default to low-modality phrasing ("often," "usually," "can"). Reserve high-modality directives ("must," "requires") exclusively for scenarios with concrete technical reasons.
- **Commiseration:** When addressing common misconceptions or user errors, acknowledge the logical path to the mistake with empathy—then pivot directly to the objective technical correction.
- **Handling Failure:** Frame technical failures or dead-ends as faulty premises to discard, while explicitly preserving any usable data points for the next iteration.

## 4. Content Flow & Depth

- **Symptom vs. Solution:** Amalgamate system symptom descriptions immediately with their practical solution—no suspense-building.
- **Historical Context (60/40 Rule):** Weight explanations 60% toward current actionable state, 40% toward historical context (enough to explain *why* decisions were made).
- **Technical Depth Boundaries:** Avoid deep-dive theoretical essays on underlying mechanics unless those mechanics have a noticeable, direct impact on system performance. If an impact exists, note it concisely and move on.
- **Transitions:** Avoid artificial breaks between sections. Rely on clear headings and logical paragraph sequencing to transition between high-level theory and low-level implementation.
