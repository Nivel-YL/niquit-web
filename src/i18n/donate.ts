// Stripe Payment Link URLs, fill in with real links from your Stripe dashboard.
// Each key is the EUR amount (base price, before VAT).
export const STRIPE_LINKS: Record<string, string> = {
  '200': 'https://buy.stripe.com/PLACEHOLDER_200',
  '150': 'https://buy.stripe.com/PLACEHOLDER_150',
  '125': 'https://buy.stripe.com/PLACEHOLDER_125',
  '100': 'https://buy.stripe.com/PLACEHOLDER_100',
  '75':  'https://buy.stripe.com/PLACEHOLDER_75',
  '50':  'https://buy.stripe.com/PLACEHOLDER_50',
  '25':  'https://buy.stripe.com/PLACEHOLDER_25',
};

// For "custom amount": create a Stripe Payment Link with "customer chooses price"
export const STRIPE_CUSTOM_LINK = 'https://buy.stripe.com/PLACEHOLDER_CUSTOM';

// Displayed tiers, descending order (large to small, deliberately, so the
// first number a visitor sees anchors high, not low. Do not resort ascending.)
export const DONATE_TIERS = [200, 150, 125, 100, 75, 50, 25] as const;
