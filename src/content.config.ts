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
    // A-H are the pipeline's topic clusters. 'S' is not a topic: it marks a
    // hand-written personal story from the author, shown with its own label.
    cluster: z.enum(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'S']).optional(),
    draft: z.boolean().default(false),
    // Cross-language identity for the rare legacy article whose slug is not
    // the same string in every language (pre-dates the "always translate
    // the English slug literally" convention). Omit it and the slug itself
    // is the identity, which is correct for every other article on the site.
    topicId: z.string().optional(),
  }),
});

export const collections = { blog };
