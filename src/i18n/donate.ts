// Stripe Payment Link URLs — one link per tier.
// Descending order matches DONATE_TIERS below (anchor high, not low).
export const STRIPE_LINKS: Record<string, string> = {
  '200': 'https://buy.stripe.com/bJe4gy80h5m79Hcd7ngIo00',
  '175': 'https://buy.stripe.com/eVqdR84O501N7z45EVgIo01',
  '150': 'https://buy.stripe.com/aFabJ05S93dZf1w6IZgIo02',
  '125': 'https://buy.stripe.com/6oUfZg4O53dZ9HcaZfgIo03',
  '100': 'https://buy.stripe.com/00wfZg5S929VaLg3wNgIo04',
  '75':  'https://buy.stripe.com/6oU00icgx4i3g5A5EVgIo05',
  '50':  'https://buy.stripe.com/7sYbJ0eoF9CnbPkgjzgIo06',
  '25':  'https://buy.stripe.com/5kQfZg94l6qbg5AebrgIo07',
};

// "Your amount" — customer types any number.
export const STRIPE_CUSTOM_LINK = 'https://buy.stripe.com/7sY4gya8p15RbPk1oFgIo08';

// Displayed tiers, descending order (large to small, deliberately, so the
// first number a visitor sees anchors high, not low. Do not resort ascending.)
export const DONATE_TIERS = [200, 150, 125, 100, 75, 50, 25] as const;
