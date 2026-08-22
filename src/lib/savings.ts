// Single source of truth for the savings maths, shared by the modal
// (Calculator.astro, client-side) and the standalone page (CalculatorPage.astro,
// both server-rendered defaults and client-side recompute). Keeping the numbers
// in one place is the whole point: a smoker who sees one figure in the hero
// modal and a different figure on /calculator would read the tool as broken.
//
// Pure and framework-agnostic: only Intl (available in Node SSR and the
// browser). No DOM, no Astro. Ported verbatim from the design prototype's
// maths: 4%/yr escalation, packsPerYear = (perDay/perPack)*365.25, past spend
// discounts today's price backwards, future saving escalates it forward.

export const ESCALATION = 0.04;
export const HORIZONS = [1, 2, 3, 5, 10, 20];

export function packsPerYear(perDay: number, perPack: number): number {
  return (Math.max(0, perDay) / Math.max(1, perPack)) * 365.25;
}

// Money already spent: today's price discounted backwards at the escalation
// rate, one term per year from startYear up to now. startYear is clamped to
// the current year (you cannot have started in the future).
export function spentSince(
  perDay: number,
  perPack: number,
  price: number,
  startYear: number,
  currentYear: number = new Date().getFullYear(),
): number {
  const ppy = packsPerYear(perDay, perPack);
  const p = Math.max(0, price);
  const years = Math.max(0, currentYear - Math.min(currentYear, startYear));
  let sum = 0;
  for (let k = 0; k < years; k++) sum += (ppy * p) / Math.pow(1 + ESCALATION, k + 1);
  return sum;
}

// Money saved over the next `horizon` years if you quit today: today's price
// escalated forward year by year.
export function savedOver(
  perDay: number,
  perPack: number,
  price: number,
  horizon: number,
): number {
  const ppy = packsPerYear(perDay, perPack);
  const p = Math.max(0, price);
  let sum = 0;
  for (let y = 0; y < horizon; y++) sum += ppy * p * Math.pow(1 + ESCALATION, y);
  return sum;
}

export function savedByHorizon(
  perDay: number,
  perPack: number,
  price: number,
): { horizon: number; amount: number }[] {
  return HORIZONS.map((h) => ({ horizon: h, amount: savedOver(perDay, perPack, price, h) }));
}

export function formatMoney(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(Math.round(n));
}

// Pluralize the year label per locale (Russian needs one/few/many: 1 год,
// 2 года, 5 лет). Falls back gracefully for one/other locales.
export function yearLabel(
  n: number,
  locale: string,
  words: { year: string; yearsFew: string; years: string },
): string {
  const c = new Intl.PluralRules(locale).select(n);
  if (c === 'one') return words.year;
  if (c === 'few') return words.yearsFew;
  return words.years;
}
