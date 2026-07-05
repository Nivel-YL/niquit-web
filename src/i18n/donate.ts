// Stripe Payment Link URLs, fill in with real links from your Stripe dashboard.
// Each key is the EUR amount (base price, before VAT).
export const STRIPE_LINKS: Record<string, string> = {
  '25':  'https://buy.stripe.com/PLACEHOLDER_25',
  '50':  'https://buy.stripe.com/PLACEHOLDER_50',
  '75':  'https://buy.stripe.com/PLACEHOLDER_75',
  '100': 'https://buy.stripe.com/PLACEHOLDER_100',
  '125': 'https://buy.stripe.com/PLACEHOLDER_125',
  '150': 'https://buy.stripe.com/PLACEHOLDER_150',
  '200': 'https://buy.stripe.com/PLACEHOLDER_200',
};

// For "custom amount": create a Stripe Payment Link with "customer chooses price"
export const STRIPE_CUSTOM_LINK = 'https://buy.stripe.com/PLACEHOLDER_CUSTOM';

// Displayed tiers, ascending order
export const DONATE_TIERS = [25, 50, 75, 100, 125, 150, 200] as const;
