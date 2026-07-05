// Stripe Payment Link URLs, fill in with real links from your Stripe dashboard.
// Each key is the EUR amount (base price, before VAT).
export const STRIPE_LINKS: Record<string, string> = {
  '200': 'https://buy.stripe.com/PLACEHOLDER_200',
  '100': 'https://buy.stripe.com/PLACEHOLDER_100',
  '50':  'https://buy.stripe.com/PLACEHOLDER_50',
  '30':  'https://buy.stripe.com/PLACEHOLDER_30',
  '10':  'https://buy.stripe.com/PLACEHOLDER_10',
  '5':   'https://buy.stripe.com/PLACEHOLDER_5',
};

// For "custom amount": create a Stripe Payment Link with "customer chooses price"
export const STRIPE_CUSTOM_LINK = 'https://buy.stripe.com/PLACEHOLDER_CUSTOM';

// Displayed tiers, order is large to small (no anchor effect)
export const DONATE_TIERS = [200, 100, 50, 30, 10, 5] as const;
