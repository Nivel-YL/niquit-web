# NiQuit Website — Claude Instructions

## Project
Static marketing site + blog for the NiQuit app. Astro v7 + Tailwind v4.
Deployed on **Cloudflare Pages** (auto-deploy from `master` branch).
Live: `https://niquit-web.pages.dev` (custom domain planned — see SESSION_STATE.md)

Old frozen site: `https://niquit.netlify.app` — Netlify credits exhausted, not updated.
App privacy/terms still link to netlify URLs — will be fixed when custom domain is set up.

## Stack
- **Astro v7** — static output, `src/content.config.ts` with `glob()` loader
- **Tailwind v4** — `@tailwindcss/vite` plugin, config lives in `src/styles/global.css` via `@theme`
- **5 languages** — en (no prefix) / ru / de / es / fr
- **Fonts** — Space Grotesk 700 (display), Figtree 400-700 (body), JetBrains Mono 400-500 (mono); loaded from Google Fonts in `src/layouts/Base.astro`

## Build & Deploy
```
npm install        # no package-lock.json in repo — always use npm install, never npm ci
npm run build      # outputs to dist/
```
Deploy is automatic: push to `master` → Cloudflare Pages builds and deploys.
Manual trigger: Cloudflare Dashboard → Workers & Pages → niquit-web → Create deployment.

**Do NOT commit package-lock.json.** It was deleted because Windows-generated lock files
break `npm ci` on Linux CI runners (Cloudflare, GitHub Actions). npm install regenerates it.

## Blog Automation
Two scripts, two GitHub Actions workflows:

**Generation** (`.github/workflows/blog-editor.yml`, Monday 09:00 UTC):
- `scripts/blog_editor.py` picks next `pending` topic from `BLOG_TOPIC_BACKLOG.md`
- Does ONE shared web research call (Haiku), then 5 parallel write calls (Sonnet 5)
- Saves 5 language .md files as `draft: true`, generates SVG cover, runs fact audit
- Commits and pushes → Cloudflare auto-deploys (drafts invisible on live site)

**Publication** (`.github/workflows/publisher.yml`, Tue + Fri 08:00 UTC):
- `scripts/publisher.py` picks first `approved` topic, flips `draft: true → false`, sets `publishDate`
- Commits and pushes → Cloudflare auto-deploys → article goes live

Manual publish: GitHub → Actions → Publisher → Run workflow.

## i18n Architecture
- `src/i18n/ui.ts` — all UI strings, 5 languages, `as const`. Type `UiStrings = typeof ui.en`.
  - **Adding a new key**: add to `en` first (sets the type), then to all other 4 langs. Missing key = TS error.
- `src/i18n/donate.ts` — Stripe payment link URLs + displayed tiers config.
- Routing: `src/pages/index.astro` (EN) + `src/pages/{ru,de,es,fr}/index.astro` etc.
- `localePath(lang, path)` builds correct URLs (EN has no prefix).

## Design Tokens (global.css @theme)
```
#0A1A33  Navy / page bg
#0F2244  Panel / dropdown bg
#FF6B5C  Coral (CTA, strikethrough)
#35C6D8  Cyan (accent, switcher)
#EAF1FF  Text primary
#93A6C6  Text muted
```
Custom Tailwind utilities created by `@theme`: `font-display`, `font-body`, `font-mono`.

## Key CSS Classes
- `.nicotine` — animated strikethrough. Timings are deliberate — do not change.
- `.phone` — hero phone mockup frame with float animation (5s ease-in-out, 14px rise).
- `.lang__*` — language dropdown (JS-driven, click-outside + Escape).

## Hero Screenshots
Per-language screenshots live in `public/img/{LANG}/{n}.jpg`.
Map is hardcoded in `src/components/pages/HomePage.astro` (`heroScreenshot` const).
To add/replace: drop file in the right folder, update the map.

## Stripe Donate
- `src/i18n/donate.ts` has `STRIPE_LINKS` (8 URLs), `STRIPE_CUSTOM_LINK`, `DONATE_TIERS`.
- `DONATE_TIERS` is display-only — tiers [200,150,125,100,75,50,25].
- The €175 Stripe link exists in `STRIPE_LINKS` but is intentionally excluded from `DONATE_TIERS`.

## Rules
- **No em-dashes** anywhere in the site — use `, ` or split sentence.
- **Non-ASCII files**: always use the Write tool. Never PowerShell `Set-Content` — adds BOM.
- **Prose links**: use `#35C6D8` not `#22D3EE` (old cyan value, now replaced).
- `DONATE_TIERS` order is descending on purpose (anchoring) — do not sort ascending.
- **Slugs**: always `entry.id.split('/').pop()` — never `entry.slug` (removed in Astro v7).

## Vercel niquit-stripe-api
Separate project at `https://niquit-stripe-api.vercel.app`. Hosts:
- `/api/coach` — AI coach proxy
- `/api/feedback` — feedback → Telegram
- `/privacy.html` — redirects to `niquit.netlify.app/privacy` (via vercel.json redirect)
Do NOT delete or rename this project.
