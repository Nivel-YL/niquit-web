// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://niquit.app',

  // Cloudflare Pages decides trailing-slash behavior purely from output file
  // layout (no config knob on their side). 'file' + 'never' makes every page
  // serve at its no-slash URL directly (200) and its slashed form redirect
  // to that URL (single 308 hop) - matching canonical/og:url/sitemap/
  // localePath(), which have always used the no-slash form.
  trailingSlash: 'never',
  build: {
    format: 'file',
  },

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
      // than the one every internal link actually points to. Also strips
      // .html/index.html - build.format:'file' makes Astro's own route URLs
      // carry the file extension, and trailingSlash:'never' should already
      // keep this clean, but this is belt-and-braces against a silently
      // wrong sitemap. Dedupes in case normalization ever collapses two
      // distinct routes onto the same URL.
      serialize: (() => {
        const seen = new Set();
        return (item) => {
          const url = new URL(item.url);
          url.pathname = url.pathname
            .replace(/(^|\/)index\.html$/, '$1')
            .replace(/\.html$/, '');
          if (url.pathname.length > 1) {
            url.pathname = url.pathname.replace(/\/$/, '');
          }
          if (url.pathname === '') url.pathname = '/';
          item.url = url.toString();
          if (seen.has(item.url)) return undefined;
          seen.add(item.url);
          return item;
        };
      })(),
    }),
  ],
});