---
title: "Building a Blog with Markdown and GitHub Pages"
date: 2026-05-19
tags: [tutorial, web, markdown]
---

# Building a Blog with Markdown and GitHub Pages

GitHub Pages serves static files — no server, no database. That makes it perfect for a lightweight Markdown blog.

## How It Works

1. **Posts are Markdown files** stored in a `/posts/` directory
2. **Frontmatter** (YAML between `---` delimiters) stores metadata like title, date, and tags
3. **marked.js** renders Markdown to HTML in the browser
4. **Fetch API** loads posts at page load — zero build tools needed

## Why Markdown?

- Write in any text editor
- Version-controlled alongside the site
- Easy to migrate to other platforms
- Human-readable even raw

## Adding a New Post

Just create a new `.md` file in `/posts/` with frontmatter at the top, then add it to `posts-index.json`. That's it.
