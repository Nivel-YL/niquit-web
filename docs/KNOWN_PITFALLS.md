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
