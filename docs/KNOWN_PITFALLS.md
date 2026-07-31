# Known Pitfalls

## Encoding
**Never use PowerShell `Set-Content` for non-ASCII files.**
PowerShell 5.1 writes UTF-16 LE with BOM by default. This corrupts ES/FR blog posts
(diacritics become garbage) and breaks Astro's parser on .astro files.
Always use the Write tool (UTF-8 no BOM) for any file containing non-ASCII characters.

If BOM is already present (EF BB BF), strip with:
```powershell
$bytes = [System.IO.File]::ReadAllBytes($path)
[System.IO.File]::WriteAllBytes($path, $bytes[3..($bytes.Length-1)])
```

## Em-Dashes
Em-dashes (`—`) are prohibited throughout the entire site — in all 5 languages.
Use `, ` or split into two sentences. `blog_editor.py` auto-replaces them before saving.

## ui.ts: as const + new fields
`ui.ts` uses `as const`. `UiStrings = typeof ui.en`.
When adding a new key to `hero` (or any section): add to EN first (defines the type),
then add to all 4 other languages before building. Missing key causes TS error.

## DONATE_TIERS order
Array is intentionally descending [200,150,125,100,75,50,25].
Anchoring effect: first number seen is highest, lowering perceived cost of smaller tiers.
Do not sort ascending. Comment in donate.ts explains this.

## €175 Stripe link
`STRIPE_LINKS` has a '175' key with a real Stripe URL.
It is intentionally absent from `DONATE_TIERS` (removed for visual fit — 7 tiers fit one row, 8 did not).
Do not delete the key from STRIPE_LINKS; just don't add '175' back to DONATE_TIERS.

## Apple Pay on checkout
Apple Pay only appears on Safari/Apple devices. It will never show on Chrome/Windows.
This is expected Stripe behavior, not a configuration bug.

## Write tool "file modified since read" error
Happens when PowerShell has touched a file externally after the last Read.
Fix: re-read the file, then write. The tool tracks file state.

## Slug extraction from content collection
`entry.id` (glob() loader) = `"ru/article-slug"` (no extension, lang prefix included).
Slug = `entry.id.split('/').pop()` → `"article-slug"`.
**`entry.slug` does NOT exist** in Astro v7 glob() loader — using it returns `undefined`,
which causes article links to resolve as `/ru/blog/undefined` → 404 → redirect to main page.
This was a real bug caught 2026-07-07 after Cloudflare Pages deployment.

## localePath trailing slash
`localePath('en', '')` → `'/'` (not `''`).
`localePath('ru', 'blog')` → `'/ru/blog'` (no trailing slash).
The function handles edge cases — do not manually build language URLs.

## package-lock.json: do NOT commit
The repo has no `package-lock.json` by design. It was deleted 2026-07-07 because:
- The Windows-generated lock file included only Win32 optional packages
- Linux CI runners (Cloudflare Pages, GitHub Actions) run `npm ci` which requires all
  platform packages to be in the lock file → fails with "missing from lock file"
- Without a lock file, both Cloudflare and GitHub Actions fall back to `npm install` ✓
If `package-lock.json` reappears locally (after `npm install`), do not commit it.
Add to `.gitignore` if it keeps appearing accidentally.

## Cloudflare Pages: npm ci vs npm install
Cloudflare Pages runs `npm ci` automatically if `package-lock.json` is present,
or `npm install` if it is not. Since the lock file is absent, it uses `npm install`.
Do not add a lock file back without regenerating it on Linux first.

## Netlify credits exhausted (management-nivel-team)
The Netlify team account ran out of credits 2026-07-07 (caused by Netlify Agent Runner usage).
All deploys to Netlify are blocked — including CLI deploys via the API (returns 403 Forbidden).
The site `niquit.netlify.app` is still live on the last cached deploy but cannot be updated.
Migration: site moved to Cloudflare Pages. Custom domain pending to unify URLs.

## Vercel niquit-stripe-api
This project must not be deleted or renamed.
It hosts the AI coach proxy, feedback endpoint, and privacy redirect.
App code hardcodes `https://niquit-stripe-api.vercel.app` in app constants.
The `/privacy.html` redirect points to `niquit.netlify.app/privacy` — update when custom domain is live.

## Cloudflare Pages serves the homepage for ANY unresolved path, never a real 404
Discovered 2026-07-25 debugging `/sitemap.xml` returning the homepage's HTML instead of XML.
There was no file literally named `sitemap.xml` (the real file is `sitemap-index.xml`), and
Cloudflare Pages' fallback for a path with no matching static asset (and no custom `404.html`)
is to serve `index.html` with status 200 — not a 404.
**This means a bare `curl -o /dev/null -w '%{http_code}'` returning 200 proves nothing.** A
totally broken route serves the same 200 as a working one. Any test of a Pages route must also
check the response body (`<title>`, `<link rel="canonical">`) — never trust status code alone.

## Cloudflare Pages: no trailing-slash config, direction is decided by file layout only
There is no setting anywhere in Cloudflare Pages to control trailing-slash redirect direction
(confirmed: it's an open community feature request, not a missing config we didn't find).
The actual behavior comes entirely from the asset resolver reading the output file layout:
`about.html` → served at `/about` (no slash); `about/index.html` → served at `/about/` (with
slash). If a page is requested in the "wrong" form for its file, Pages 308-redirects to the
form its file layout actually produces.
Astro's `build.format` controls exactly this: `'directory'` (Astro's default) emits
`page/index.html` (slash-served); `'file'` emits `page.html` (no-slash-served). Pair
`build.format:'file'` with `trailingSlash:'never'` for a fully no-slash site (this project's
current config) — Astro's own docs recommend this pairing, and `@astrojs/sitemap` also detects
this exact config and special-cases the sitemap's root `<loc>` entry (strips even the bare `/`)
to match.
**Do not fight this with a Pages Function/middleware instead of fixing the file layout** — see
the next entry.

## Adding a Cloudflare Pages Function that redirects one direction, while the file layout still produces the other direction, is an infinite redirect loop
2026-07-25: added `functions/_middleware.js` to 301-redirect `/path/` → `/path`, while the site
was still built with `build.format:'directory'` (which makes Cloudflare's own resolver
308-redirect `/path` → `/path/`). Tested clean locally via `wrangler pages dev` + Playwright
across 13 pages. **In actual production, `/method` hung 45+ seconds and was unreachable in
both forms** — local wrangler emulation did not reproduce the failure at all. Root cause:
Cloudflare's resolver and the Function were each redirecting in the opposite direction, so a
request bounced between the two forever (or until the platform's own timeout killed it).
Had to be reverted (`git revert`) to restore the site.
**Fix that actually worked** (no middleware at all): change `build.format` to make Astro's own
output match the desired direction (see previous entry). One layout, one resolver, no second
actor — a loop becomes structurally impossible.
**Prevention:** never add a Pages Function to override trailing-slash/redirect behavior without
first checking whether the platform's own behavior (driven by file layout, here) already
conflicts with it. If you must add Function-based redirect logic for anything, test it against
a real Cloudflare Pages preview deployment (`*.pages.dev`, built by an actual push) before
merging — local `wrangler pages dev` did not catch this loop.

## hreflang tags with a double slash from feeding a leading-slash path into localePath()
`localePath(lang, path)` (`src/i18n/ui.ts`) builds its own leading slash — it expects a bare
path like `'method'` or `''`, never `'/method'`. `Base.astro`'s hreflang block used to derive
its input by regex-stripping the locale prefix directly off `Astro.url.pathname` (which starts
with `/`), leaving a leading slash in what got passed to `localePath()`. Result, live in
production for an unknown period until caught 2026-07-25: every hreflang tag on every
translated nested page read `https://niquit.app//method` (double slash), for every locale.
**Fix:** `stripLocalePrefix()` in `src/i18n/ui.ts` strips both the locale prefix and the leading
slash, returning the bare form `localePath()` expects. Used in `Base.astro`'s hreflang block and
`Header.astro`'s language-switcher href — anywhere a "current path with locale/extension
stripped" is needed for `localePath()`, use `stripLocalePrefix(canonicalPath(Astro.url))`, not a
one-off regex.
