import { getCollection, type CollectionEntry } from 'astro:content';
import { LANGS, type Lang } from '../i18n/ui';

/**
 * Resolves, for a given blog entry, which of the 5 languages actually have a
 * live (non-draft) version of "the same article" and what that version's
 * real slug is. Matching key is entry.data.translationKey when set (needed
 * only when a translation's slug genuinely differs from the others), falling
 * back to the entry's own slug otherwise, which is always correct for
 * pipeline-generated content since publisher.py publishes all 5 languages
 * under one shared, English-derived slug.
 *
 * Returns only languages that actually exist, no entry is emitted for a
 * language with no matching live page.
 */
export async function getBlogAlternates(
  entry: CollectionEntry<'blog'>,
): Promise<Partial<Record<Lang, string>>> {
  const ownSlug = entry.id.split('/').pop() ?? entry.id;
  const key = entry.data.translationKey ?? ownSlug;

  const allPosts = await getCollection('blog', (e) => !e.data.draft);

  const alternates: Partial<Record<Lang, string>> = {};
  for (const post of allPosts) {
    const postSlug = post.id.split('/').pop() ?? post.id;
    const postKey = post.data.translationKey ?? postSlug;
    if (postKey === key && LANGS.includes(post.data.lang)) {
      alternates[post.data.lang] = postSlug;
    }
  }
  return alternates;
}
