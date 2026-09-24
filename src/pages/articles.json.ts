import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

// Lightweight per-language article index for the app's Home screen (random
// blog article card, replacing the old static daily quote). Static JSON,
// built once at deploy time like every other page on this site - no server,
// no per-request work.
export const prerender = true;

type ArticleEntry = {
  slug: string;
  title: string;
  description: string;
  cluster: string | null;
  publishDate: string;
};

export const GET: APIRoute = async () => {
  const posts = await getCollection('blog', (e) => !e.data.draft);
  const byLang: Record<string, ArticleEntry[]> = { en: [], ru: [], de: [], es: [], fr: [] };

  for (const post of posts) {
    const lang = post.data.lang;
    if (!(lang in byLang)) continue;
    byLang[lang].push({
      slug: post.id.split('/').pop()!,
      title: post.data.title,
      description: post.data.description,
      cluster: post.data.cluster ?? null,
      publishDate: post.data.publishDate.toISOString(),
    });
  }

  for (const lang of Object.keys(byLang)) {
    byLang[lang].sort((a, b) => b.publishDate.localeCompare(a.publishDate));
  }

  return new Response(JSON.stringify(byLang), {
    // Public, read-only, no sensitive data - fetched cross-origin from the
    // app (and Expo's web export target), so this needs to be open.
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
  });
};
