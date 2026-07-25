// Cloudflare Pages Function, runs on every request before static asset serving.
// The site's canonical URL form has no trailing slash (see Base.astro /
// astro.config.mjs sitemap serialize()), but Astro's directory-format build
// still makes /page/ resolve to the same file as /page with no redirect
// between them. Redirect the slashed form to match, so it isn't a second
// indexable URL for the same content.
export const onRequest = async (context) => {
  const url = new URL(context.request.url);

  if (url.pathname.length > 1 && url.pathname.endsWith('/')) {
    url.pathname = url.pathname.replace(/\/+$/, '');
    return Response.redirect(url.toString(), 301);
  }

  return context.next();
};
