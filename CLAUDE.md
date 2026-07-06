# NiQuit Website — Claude Instructions

## Project
Static marketing site for the NiQuit app. Astro v7 + Tailwind v4.
Deployed on **Netlify** (drag `dist/` to dashboard — no CI yet).
Live: `https://niquit.netlify.app`

## Stack
- **Astro v7** — static output, `src/content.config.ts` with `glob()` loader
- **Tailwind v4** — `@tailwindcss/vite` plugin, config lives in `src/styles/global.css` via `@theme`
- **5 languages** — en (no prefix) / ru / de / es / fr
- **Fonts** — Space Grotesk 700 (display), Figtree 400-700 (body), JetBrains Mono 400-500 (mono); loaded from Google Fonts in `src/layouts/Base.astro`

## Build & Deploy
```
npx astro build        # outputs to dist/
```
Then drag `dist/` to the Netlify "niquit" project dashboard. No CLI deploy configured.

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
- Stripe account under review (Nivexon OÜ) — live payments pending approval.

## Rules
- **No em-dashes** anywhere in the site — use `, ` or split sentence.
- **Non-ASCII files**: always use the Write tool. Never PowerShell `Set-Content` — adds BOM.
- **Prose links**: use `#35C6D8` not `#22D3EE` (old cyan value, now replaced).
- `DONATE_TIERS` order is descending on purpose (anchoring) — do not sort ascending.

## Vercel niquit-stripe-api
Separate project at `https://niquit-stripe-api.vercel.app`. Hosts:
- `/api/coach` — AI coach proxy
- `/api/feedback` — feedback → Telegram
- `/privacy.html` — redirects to `niquit.netlify.app/privacy` (via vercel.json redirect)
Do NOT delete or rename this project.
