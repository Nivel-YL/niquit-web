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
Use `, ` or split into two sentences. Caused confusion with smart-quotes in some editors.

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

## Stripe account under review
Account (Nivexon OÜ) was under 2-3 day review as of 2026-07-06.
Until approved, payment links exist but live charges do not process.
No code change needed — Stripe activates automatically on approval.

## Write tool "file modified since read" error
Happens when PowerShell has touched a file externally after the last Read.
Fix: re-read the file, then write. The tool tracks file state.

## Slug extraction from content collection
`entry.id` = `"en/why-nicotine-is-different"`. Slug = `entry.id.split('/').pop()`.
Do NOT use `entry.slug` — removed in Astro v7 glob() loader.

## localePath trailing slash
`localePath('en', '')` → `'/'` (not `''`).
`localePath('ru', 'blog')` → `'/ru/blog'` (no trailing slash).
The function handles edge cases — do not manually build language URLs.

## Vercel niquit-stripe-api
This project must not be deleted or renamed.
It hosts the AI coach proxy, feedback endpoint, and privacy redirect.
App code hardcodes `https://niquit-stripe-api.vercel.app` in `ember/constants/config.ts`.
