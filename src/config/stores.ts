import type { Lang } from '../i18n/ui';

export const GOOGLE_URL = 'https://play.google.com/store/apps/details?id=com.niquit.app';
export const APPLE_URL  = 'https://apps.apple.com/app/id6781069151';

// Store pages in the site's language. Google: hl picks the listing language.
// Apple: the country storefront picks it (a bare link lands on the US page in
// English); the App Store app on an iPhone still opens the person's own store.
const APPLE_STOREFRONT: Record<Lang, string> = { en: 'us', ru: 'ru', de: 'de', es: 'es', fr: 'fr' };

export const googleUrl = (lang: Lang) => `${GOOGLE_URL}&hl=${lang}`;
export const appleUrl = (lang: Lang) => `https://apps.apple.com/${APPLE_STOREFRONT[lang]}/app/id6781069151`;
