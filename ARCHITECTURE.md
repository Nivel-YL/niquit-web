# Architecture

## File Tree (src/)

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
    BlogCard.astro        ← card for blog list
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
    blog/[slug].astro     ← EN blog post (slug = filename without .md)
    {ru,de,es,fr}/        ← same structure, lang prefix
  content/
    blog/
      en/  de/  es/  fr/  ru/   ← .md files, all draft:true currently
  content.config.ts       ← glob() loader, schema: title/description/publishDate/lang/draft/heroImage
```

## Multilingual Routing

EN has no URL prefix. Other langs: `/ru/`, `/de/`, `/es/`, `/fr/`.

```ts
localePath('en', 'blog')  → '/blog'
localePath('ru', 'blog')  → '/ru/blog'
```

Pages are duplicated manually per lang (not dynamic `[lang]` routes).
`getLangFromUrl(url)` extracts lang from pathname.

## Hero Layout

```
<section radial-gradient full-width>
  <div max-w-5xl mx-auto grid gap-8 md:grid-cols-[1.05fr_0.95fr]>
    <div>  ← text: label, h1 with .nicotine span, sub, coral CTA → Play Store
    <div>  ← phone: .phone div with per-lang screenshot
```

Phone screenshot path resolved at build time from `heroScreenshot[lang]` map.

## Fonts

Loaded in `Base.astro` from Google Fonts. Applied via CSS variables:
- `--font-display: 'Space Grotesk'` → Tailwind `font-display`
- `--font-body: 'Figtree'` → applied to `html` element
- `--font-mono: 'JetBrains Mono'` → Tailwind `font-mono`

Montserrat still in Google Fonts URL for fallback (legacy inline styles in some components).

## Donate Flow

```
DONATE_TIERS [200,150,125,100,75,50,25]
  → DonateSection renders tier buttons
  → each links to STRIPE_LINKS[String(amount)]
  → opens buy.stripe.com hosted checkout page
  → no backend needed
```

Custom amount → STRIPE_CUSTOM_LINK (Stripe "customer chooses price").

## Content Collections

`src/content.config.ts` uses `glob()` loader. Blog entries accessed via `getCollection('blog')`.
Slug = `entry.id.split('/').pop()` (filename without extension).
Filter by lang: `entry.data.lang === lang`.
All posts currently `draft: true` — not shown on homepage or blog list.
