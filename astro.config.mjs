// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://niquit.app',

  vite: {
    plugins: [tailwindcss()],
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ru', 'de', 'es', 'fr'],
    routing: {
      prefixDefaultLocale: false,
    },
  },

  integrations: [
    sitemap({
      // Match the site's own link convention (localePath() never adds a
      // trailing slash) so the sitemap doesn't advertise a different URL
      // than the one every internal link actually points to.
      serialize(item) {
        const url = new URL(item.url);
        if (url.pathname.length > 1) {
          url.pathname = url.pathname.replace(/\/$/, '');
        }
        item.url = url.toString();
        return item;
      },
    }),
  ],
});