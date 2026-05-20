---
title: Getting Started with the jdk-bug Homepage
date: 2026-05-19
tags: [tutorial, homepage]
---

# Getting Started

The jdk-bug homepage is a static site hosted on **GitHub Pages**. Here's what powers it.

## Tech Stack

- **HTML5** — semantic structure
- **CSS3** — custom properties for theming
- **Vanilla JS** — no frameworks, no build tools
- **marked.js** — Markdown rendering in the browser

## Themes

The site supports three themes:

| Theme | Emoji | Description |
|-------|-------|-------------|
| Light | ☀️ | Clean, bright default |
| Dark | 🌙 | Easy on the eyes |
| Vaporwave | 🌴 | Neon pink and cyan vibes |

Toggle between them using the button in the top-right corner.

## Blog

This blog section fetches Markdown files from the `/posts/` directory and renders them client-side. Each post has YAML frontmatter for metadata:

```yaml
---
title: My Post Title
date: 2026-05-19
tags: [tutorial, homepage]
---
```

That's it — simple, fast, and no build step required.
