---
name: book-to-share-pdf
description: Use this skill when the user gives a book title and asks to 拆书, 解构一本书, 做读书分享, 读书会分享, 讲给别人听, 写分享稿, or generate a PDF reading booklet. Research reliable public sources first, seek legal full text or substantial previews when needed, decide the best sharing strategy for the book type, then produce one Chinese, story-driven, source-grounded, old-paper-style PDF booklet. Do not use for engineering textbooks, programming manuals, paper reviews, pure purchase links, simple catalog lookup, translation-only tasks, mind maps, or slide decks unless explicitly asked.
---

# Book-to-Share PDF Skill

## Purpose

Turn a book title into a Chinese PDF reading booklet that helps the user share the book with others.

The goal is not to summarize a book mechanically. The goal is to understand the book, judge how it should be told, and transform it into a story-driven, source-grounded, readable booklet that can support oral sharing, article sharing, or a reading-club discussion.

Default voice:

> 会讲故事的读书人。

This means: clear, humane, thoughtful, vivid, but not sensationalized; grounded in sources, but not academic and stiff.

## Final Deliverable

Produce exactly one final user-facing artifact by default:

```text
《书名》拆书分享小册.pdf
```

Intermediate files may be created during work, for example:

```text
draft.md
booklet.html
booklet.pdf
sources.json
```

But only the final PDF should be presented to the user unless they explicitly ask for drafts, source files, or implementation details.

## Default Language

Use Chinese by default.

If the original book is in another language, keep original names or key terms where useful, but explain them in Chinese.

## Operating Principles

### 1. Research before writing

Do not rely only on model memory when the user provides only a book title.

Before drafting the booklet, research reliable materials such as:

- Publisher page
- Official author page
- Author interviews, lectures, essays, podcasts, or public talks
- Table of contents
- Official description
- Legal previews or excerpts
- Public-domain full text, when applicable
- Library or database records, when available
- Serious reviews from reputable media, journals, scholars, or established book-review platforms
- Reader reviews only as supplementary evidence, never as the main factual base

For detailed research rules, read `references/research_rules.md`.

### 2. Confirm the exact book

Many books have similar or identical titles. First identify:

- Chinese title
- Original title, if any
- Author
- Translator, if relevant
- Publisher or edition used
- Publication year
- Whether the book is fiction, nonfiction, essay collection, academic work, biography, etc.

If there are multiple plausible books and the user did not specify which one, make a best-effort choice using context. If ambiguity remains, state the selected version clearly inside the PDF.

### 3. Use legal and reliable materials

If public information is insufficient, try to locate legal full text, substantial previews, authorized excerpts, or public-domain versions.

Allowed material types include:

- Public-domain text
- Official publisher previews
- Authorized excerpts
- Author-posted material
- Library-accessible metadata or previews
- Legitimate book platform previews
- Serious secondary sources

Do not rely on obviously pirated full-text copies as the default source.

### 4. Do not pretend to have read the full book

If only public summaries, reviews, interviews, or partial previews are available, do not write as if the full text has been fully read.

Clearly distinguish:

- Confirmed facts
- Source-supported interpretation
- Reasonable inference
- Insufficient information

If the material is not enough for a full reconstruction, mark the booklet as:

```text
公开资料版拆解，尚不足以替代全文精读。
```

### 5. Shareability is the main standard

Every section should help the user explain the book to someone else.

Avoid:

- Chapter-by-chapter mechanical summary
- Dry academic overview
- Empty inspirational language
- Marketing-style exaggeration
- Unsupported claims
- Overloaded quotations
- Excessive name-dropping

Prefer:

- A strong central question
- Conflict and tension
- Clear argument flow
- Story, scene, or example
- Memorable but restrained phrasing
- Practical sharing cues
- Honest limits and caveats

## Work Process

Follow this sequence unless the user gives a stronger instruction.

### Step 1: Identify the book

Determine the exact book and edition as far as possible.

Record:

- Book title
- Original title
- Author
- Translator
- Publisher
- Year
- Genre/type
- Known editions or translation differences

### Step 2: Research and source assessment

Collect enough source material to support a responsible booklet.

Create an internal source assessment with:

- Source title
- Source type
- Reliability level
- What it supports
- Whether it gives direct access to content, such as table of contents, excerpts, or full text

Suggested reliability tiers:

1. Primary source: book text, official excerpt, author interview, publisher page
2. Strong secondary source: reputable review, academic article, serious media review
3. Weak secondary source: casual blog post, short platform summary, anonymous notes
4. Reader signal: reviews and comments, useful for reception but not for factual claims

### Step 3: Decide whether more text is needed

Judge whether the available sources are enough.

If enough:

- Proceed with a public-source-based booklet.

If not enough:

- Search for legal full text, authorized excerpts, public-domain versions, or more substantial previews.

If still not enough:

- Continue with a limited booklet only if useful.
- Clearly label its limits.
- Do not fabricate details.

### Step 4: Classify the book type

Classify the book into one or more of these types:

- 思想哲学型
- 社科洞察型
- 历史叙事型
- 商业管理型
- 人物传记型
- 文学小说型
- 心理成长型
- 投资财经型
- 文化评论型
- 经典名著型

Mixed classifications are allowed, for example:

```text
社科洞察型 + 文化评论型
```

For type-specific guidance, read `references/book_type_strategy.md`.

### Step 5: Choose the expression strategy

Select the best way to tell this book.

Available strategies:

- 冲突型: for philosophy, social criticism, intellectual tension, moral dilemma
- 故事型: for fiction, biography, history, personal growth
- 问题型: for theory, social science, psychology, management
- 案例型: for business, investing, management, applied nonfiction
- 命运型: for literature, biography, historical figures
- 观点型: for essays, cultural criticism, idea-heavy books
- 读书会讨论型: for books with open questions and interpretive space

Always include this judgment in the booklet:

```text
这本书适合怎么讲。
这本书不适合怎么讲。
```

Example:

```text
这本书不适合按章节复述。它更适合用一个核心冲突来讲，因为它真正有传播力的部分不是知识点，而是问题感。
```

### Step 6: Build the serious decomposition

Answer these questions before writing the shareable prose:

- What is the book really about?
- What central question is it trying to answer?
- Why did the author write it?
- What is the book's structure or narrative logic?
- What are the 3 to 7 most shareable ideas?
- What examples, scenes, arguments, or historical context support those ideas?
- What is easily misunderstood?
- What are the book's limits, blind spots, or controversies?
- Why does this book still matter to the intended reader now?

### Step 7: Translate the decomposition into a shareable narrative

Write the main sharing essay as if the user will tell it to others.

The main essay should have:

- A hook at the beginning
- A real problem or conflict
- A reason this book appears at this moment
- A clear explanation of the book's main line
- The most shareable ideas woven into the narrative
- Examples, scenes, author background, or historical context when helpful
- A sober note on limits or controversy
- A closing that leaves the reader with a question, judgment, or aftertaste

Do not force a fixed length. Make it complete enough for sharing. The user can delete later.

## PDF Content Structure

The PDF should follow this structure by default.

### 1. Cover

Include:

- Book title
- Author
- Subtitle for the booklet
- Book decomposition type
- Date generated
- One short hook sentence

Tone: quiet, bookish, restrained, like an old book flyleaf.

### 2. 拆书前判断

Include:

- Book type
- Best expression strategy
- Why this strategy fits
- How not to tell this book
- Whether public sources are enough
- Whether full text, excerpt, or secondary sources were used
- Confidence level

Use one of these confidence labels:

- 高: substantial primary material or full text available
- 中: reliable public sources and excerpts are sufficient for the main argument
- 低: public sources are limited; interpretation should be treated as preliminary

### 3. 一句话讲透这本书

Write no more than 200 Chinese characters.

This should be the book's central switch, not a bland summary.

It should contain judgment and tension.

### 4. 全书主线

Reconstruct the book according to reader understanding, not necessarily chapter order.

Recommended flow:

1. What question the book starts from
2. What contradiction the author sees
3. How the author develops the argument or story
4. Where the book finally lands
5. Why it matters now

### 5. 最值得传播的观点

Choose 3 to 7 ideas.

For each idea, include:

- Idea title
- Explanation
- Source basis or book basis
- How to say it when sharing
- Likely misunderstanding

### 6. 故事化分享稿

This is the main body.

It should be directly usable for oral sharing, article adaptation, or reading-club introduction.

Avoid repetitive structure like:

```text
第一章讲……第二章讲……第三章讲……
```

Prefer narrative structure:

```text
开场问题 -> 现实冲突 -> 引出本书 -> 展开核心观点 -> 穿插故事/案例/背景 -> 回到读者处境 -> 诚实指出局限 -> 有余味地收束
```

### 7. 分享提示

Keep this practical and concise.

Include:

- Best opening line for oral sharing
- Possible article titles
- Reading-club questions
- Parts that can be cut
- Parts that should not be cut

### 8. 资料来源

Place all sources at the end.

For each source, include:

- Source title
- Publisher/platform/author if available
- URL or bibliographic detail if available
- What the source supports
- Access date if relevant

Do not clutter the body with dense citations. But make important claims traceable through the source list.

## PDF Visual Style

Default style name:

```text
旧书页 · 读书人手稿风
```

Use `references/pdf_style_guide.md` for the full visual system.

Defaults:

- A5 portrait
- Warm old-paper background
- Serif/Song-style Chinese typography
- Low-saturation brown palette
- Subtle paper texture
- Readable line height and margins
- Source list preserved at the end

## Implementation Guidance

Recommended skill folder:

```text
book-to-share-pdf/
├── SKILL.md
├── references/
│   ├── book_type_strategy.md
│   ├── research_rules.md
│   └── pdf_style_guide.md
├── assets/
│   ├── paper_texture.svg
│   └── style.css
└── scripts/
    ├── build_booklet_pdf.py
    └── verify_pdf.py
```

### Suggested internal files

- `draft.md`: complete booklet content in Markdown
- `sources.json`: structured source list and confidence assessment
- `booklet.html`: styled HTML before PDF rendering, optional
- `booklet.pdf`: generated final PDF

### PDF generation

Use the included script when deterministic local generation is needed:

```bash
python scripts/build_booklet_pdf.py draft.md -o booklet.pdf
python scripts/verify_pdf.py booklet.pdf --render
```

Verify:

- PDF exists
- PDF has pages
- Chinese characters render correctly
- No obvious overflow
- Sources section is included
- Final file name is clear

## Quality Checklist

Before final delivery, check the following.

### Content

- The exact book and edition are identified as well as possible
- The sources are reliable enough for the claimed level of analysis
- The booklet states whether it is based on full text, excerpts, or public sources
- The book's central question is clear
- The book type and expression strategy are explicit
- The 3 to 7 shareable ideas are strong and not generic
- The main sharing essay is usable, not just notes
- Limits, disputes, or blind spots are acknowledged
- The source list is preserved at the end

### Expression

- The opening has a hook
- The narrative has tension
- The explanation is understandable to non-specialists
- The tone is thoughtful but not stiff
- There is no unsupported sensationalism
- There is no fake certainty
- The language sounds like a person sharing a book, not a machine summarizing chapters

### PDF

- A5 portrait format unless otherwise requested
- Warm old-paper look
- Readable Chinese font
- Page texture is subtle
- No text overflow
- Page numbers work
- The PDF can be opened normally

## Failure and Degradation Rules

If the task cannot be completed fully, still produce the best useful result without pretending.

### If the book is ambiguous

State which book was selected and why.

### If sources are thin

Create a limited public-source version and label it clearly.

### If no reliable source is found

Do not fabricate a booklet. Instead, explain what was found, why it is insufficient, and what the user can provide to continue, such as table of contents, excerpts, notes, or a legal text copy.

### If PDF generation fails

Try one alternate generation path.

If PDF still fails, preserve the complete Markdown draft and explain that PDF generation failed, including the likely cause and the file that was produced instead.

## User-Facing Final Response

When the PDF is ready, respond briefly in Chinese.

Include:

- A link to the generated PDF
- A short note on whether it is based on full text, excerpts, or public sources
- Any major limitation that matters

Do not paste the whole booklet into chat unless the user asks.
