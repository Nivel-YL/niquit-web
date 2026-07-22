import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishDate: z.date(),
    lang: z.enum(['en', 'ru', 'de', 'es', 'fr']),
    heroImage: z.string().optional(),
    draft: z.boolean().default(false),
    // Only needed when a translation's slug genuinely differs from the other
    // languages' (pipeline-generated articles never need this, publisher.py
    // always publishes all 5 languages under one shared, English-derived
    // slug). Entries sharing the same translationKey are treated as the same
    // article across languages for hreflang purposes, regardless of slug.
    translationKey: z.string().optional(),
  }),
});

export const collections = { blog };
