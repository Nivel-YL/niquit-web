# Session State — 2026-07-06

## что сделано в этой сессии

| commit | что |
|--------|-----|
| `731849b` | hero 2-col layout, JS lang switcher (SVG globe, aria, click-outside), remove footer switcher, fonts (Space Grotesk/Figtree/JetBrains Mono), `.nicotine` + `.phone` CSS |
| `8a0ae2a` | per-language hero screenshots: EN/1.jpg RU/3.jpg DE/4.jpg ES/4.jpg FR/4.jpg |
| `fc20e42` | phone float animation (5s, 14px rise, shadow lifts), max-w-5xl hero wrapper |
| `bf4169e` | Stripe payment links wired (donate.ts) |
| `9a93f07` | remove €175 tier, "Your amount" → subtle text link |

Все изменения **задеплоены на Netlify** (пользователь задеплоил вручную).

## текущее состояние по пунктам

### ✅ готово
- Сайт живой: `https://niquit.netlify.app`
- Hero: 2-col, Space Grotesk h1, `.nicotine` анимация, плавающий телефон, coral CTA → Google Play
- Языковой переключатель: JS dropdown, SVG глобус, 4 языка, Escape/click-outside
- Per-language hero screenshots (5 языков)
- Donate: 7 тиров + кастом, все Stripe links живые
- Privacy redirect: `niquit-stripe-api.vercel.app/privacy.html` → `niquit.netlify.app/privacy`
- Store privacy URL обновлён (пользователь сделал)

### 🕐 ожидает внешнего события
- **Stripe account verification** — Nivexon OÜ, ~2-3 дня с 06.07. Код готов, ничего менять не нужно.

### 📋 backlog (не блокирует)
- **og:image** — meta-тег есть в Base.astro (prop `ogImage`), но изображение не создано и не передаётся ни на одну страницу. Нужно: создать OG-изображение + передать `ogImage` в каждый `<Base>`.
- **Support page** — сейчас только DonateSection. Нужно: история, зачем бесплатно, на что идут деньги. Работа для маркетолога.
- **Blog posts** — 5 статей, все `draft: true`. Решить когда публиковать (хотя бы одну).
- **€175** — Stripe ссылка существует в `STRIPE_LINKS['175']` но не показывается. При желании добавить обратно: вставить 175 в `DONATE_TIERS` между 200 и 150.

## ключевые файлы

| файл | роль |
|------|------|
| `src/i18n/ui.ts` | все UI-строки, 5 языков |
| `src/i18n/donate.ts` | Stripe links + тиры |
| `src/styles/global.css` | design tokens, анимации |
| `src/layouts/Base.astro` | SEO, шрифты, hreflang |
| `src/components/pages/HomePage.astro` | hero + карта скриншотов |
| `src/components/Header.astro` | nav + JS lang switcher |
| `src/components/DonateSection.astro` | блок доната |
| `public/img/{LANG}/{n}.jpg` | per-language hero screenshots |

## design tokens (только в коде)

```
#0A1A33  navy bg
#0F2244  panel/dropdown bg
#FF6B5C  coral (CTA, strikethrough)
#35C6D8  cyan accent
#EAF1FF  text primary
#93A6C6  text muted
```

Шрифты: Space Grotesk (display) / Figtree (body) / JetBrains Mono (mono).

## hero hero screenshot map

```ts
en → /img/EN/1.jpg
ru → /img/RU/3.jpg
de → /img/DE/4.jpg
es → /img/ES/4.jpg
fr → /img/FR/4.jpg
```

## stripe links summary

Тиры: 200, 150, 125, 100, 75, 50, 25 EUR + custom (customer chooses).
Все ссылки в `src/i18n/donate.ts`. Аккаунт на проверке, заработают автоматически.
