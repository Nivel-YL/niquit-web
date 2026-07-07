# Architecture

## File Tree (src/ + scripts/)

```
src/
  i18n/
    ui.ts           ← all UI strings, 5 langs, as const
    donate.ts       ← Stripe links + DONATE_TIERS config
  styles/
    global.css      ← Tailwind @import, @theme tokens, custom CSS
  layouts/
    Base.astro      ← <html>, SEO, canonical, hreflang, Google Fonts, Header+Footer
    BlogPost.astro  ← blog article wrapper (prose styles)
  components/
    Header.astro          ← sticky nav, JS lang switcher (SVG globe, dropdown)
    Footer.astro          ← logo, links, copyright
    InstallButton.astro   ← Google Play link (SHOW_APPLE=false until iOS live)
    DonateSection.astro   ← tier buttons → Stripe links, custom amount link
    BlogCard.astro        ← card for blog list (slug via post.id.split('/').pop())
    ArticleCTA.astro      ← end-of-article download CTA
    pages/
      HomePage.astro      ← hero (2-col grid + phone mockup), features, blog preview, donate
      MethodPage.astro    ← 4 narrative sections (trap/why/understanding/what)
      SupportPage.astro   ← just wraps DonateSection (needs content work)
      BlogListPage.astro  ← blog index
      BlogPostPage.astro  ← single post renderer
  pages/
    index.astro           ← EN homepage
    method.astro          ← EN method
    support.astro         ← EN support
    privacy.astro         ← EN privacy policy
    terms.astro           ← EN terms
    blog/index.astro      ← EN blog list
    blog/[slug].astro     ← EN blog post
    {ru,de,es,fr}/        ← same structure, lang prefix
  content/
    blog/
      en/  de/  es/  fr/  ru/   ← .md files, draft:true (hidden) or draft:false (live)
  content.config.ts       ← glob() loader, schema: title/description/publishDate/lang/draft/heroImage

scripts/
  blog_editor.py   ← AI article generation (research → write × 5 langs → audit → SVG)
  publisher.py     ← promotes approved articles (draft:true → false, sets publishDate)

.github/workflows/
  blog-editor.yml  ← cron Monday 09:00 UTC, BATCH_SIZE=3, manual dispatch
  publisher.yml    ← cron Tue+Fri 08:00 UTC, PUBLISH_COUNT=1, manual dispatch

docs/
  CONTENT_RELIABILITY_SPEC.md  ← research rules, fact discipline, audit spec
  CONTENT_VOICE_GUIDE.md       ← writing tone per lang
  KNOWN_PITFALLS.md            ← this project's gotchas
  fact-audits/{slug}/{lang}.md ← AI fact audit reports (generated, not committed yet)

public/
  images/blog/{slug}.svg  ← generated SVG covers (navy gradient + cluster emoji)
  img/{LANG}/{n}.jpg      ← per-language hero screenshots

BLOG_TOPIC_BACKLOG.md    ← topic queue with status + cluster
AI_EDITOR_AUTOMATION_SPEC.md  ← full blog automation spec
```

## Deployment

```
GitHub push to master
  → Cloudflare Pages auto-build (npm install && npm run build → dist/)
  → Live at niquit-web.pages.dev (custom domain pending)
```

No `package-lock.json` in repo — deleted because Windows lock files break Linux CI.
Cloudflare Pages build settings: build command `npm run build`, output dir `dist`, Node 22.

## Blog Automation Flow

```
BLOG_TOPIC_BACKLOG.md (pending topics)
  ↓  blog-editor.yml (Monday cron)
  ↓  blog_editor.py:
       1. research_shared()        — 1 Haiku call + web search (max 3 uses)
       2. research_lang_specific() — targeted search for ru/de if needed
       3. process_language() × 5  — parallel Sonnet 5 write calls
          a. write_article()       — receives shared_facts + lang_specific addon
          b. fix_em_dashes()       — auto-replace — → ,  (always safe)
          c. style_check()         — flag banned phrases in frontmatter
          d. save to src/content/blog/{lang}/{slug}.md  (draft: true)
          e. audit_article()       — Haiku fact audit → docs/fact-audits/{slug}/{lang}.md
       4. generate_svg()           — deterministic SVG cover (cluster emoji, navy bg)
       5. commit all files
  ↓  Cloudflare deploys (drafts invisible on live site)
  ↓  human reviews Russian version, approves in BLOG_TOPIC_BACKLOG.md (status: approved)
  ↓  publisher.yml (Tue+Fri cron)
  ↓  publisher.py:
       1. find first approved topic
       2. flip draft: true → false in all 5 lang files
       3. set publishDate to today
       4. update backlog status → published
       5. commit and push
  ↓  Cloudflare deploys → article live on site
```

## Multilingual Routing

EN has no URL prefix. Other langs: `/ru/`, `/de/`, `/es/`, `/fr/`.

```ts
localePath('en', 'blog')  → '/blog'
localePath('ru', 'blog')  → '/ru/blog'
```

Pages are duplicated manually per lang (not dynamic `[lang]` routes).

## Content Collections

`src/content.config.ts` uses `glob()` loader (Astro v5+ API).
- `entry.id` = `"ru/article-slug"` (path relative to base, no extension)
- Slug = `entry.id.split('/').pop()` (filename without lang prefix)
- `entry.slug` does NOT exist in glob() loader — use `entry.id`
- Filter by lang: `entry.data.lang === lang`
- Filter published: `!entry.data.draft`

## SVG Cover Generation

`generate_svg(topic_id, cluster)` in `blog_editor.py`:
- Deterministic: same topic_id always produces same visual (MD5 seed for position/rotation)
- Cluster emoji: A=🍃 B=💨 C=🚬 D=🎯 E=🧠 F=❤️ G=⚡ H=🔮
- Output: `public/images/blog/{slug}.svg`
- Rendered as `heroImage` in article frontmatter

## Fonts

Loaded in `Base.astro` from Google Fonts. Applied via CSS variables:
- `--font-display: 'Space Grotesk'` → Tailwind `font-display`
- `--font-body: 'Figtree'` → applied to `html` element
- `--font-mono: 'JetBrains Mono'` → Tailwind `font-mono`

## Donate Flow

```
DONATE_TIERS [200,150,125,100,75,50,25]
  → DonateSection renders tier buttons
  → each links to STRIPE_LINKS[String(amount)]
  → opens buy.stripe.com hosted checkout page
  → no backend needed
```

Custom amount → STRIPE_CUSTOM_LINK (Stripe "customer chooses price").
