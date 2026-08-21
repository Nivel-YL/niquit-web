// Cloudflare Pages runs this on every request to the project, regardless of
// which attached domain received it. public/_redirects can't handle either
// job below - Cloudflare doesn't apply _redirects host rules to a project's
// own pages.dev domain or to its attached custom domains, and _redirects has
// no way to express "collapse repeated slashes" for an arbitrary, growing
// set of blog slugs.
//
// 1. Redirect the platform's own niquit-web.pages.dev subdomain to the real
//    site. That subdomain can't be turned off (every Pages project has one).
//    (2026-08-15 investigation: niquit-web.pages.dev was fully live and
//    crawlable, canonical tags pointed at niquit.app but Google doesn't
//    always defer to a declared canonical over an actually-crawlable
//    duplicate.)
// 2. Collapse repeated slashes (e.g. /de//blog/x). localePath() itself was
//    fixed 2026-07-25/26 to never emit these (stripLocalePrefix() is applied
//    at every current call site), but URLs it emitted before that fix are
//    still live in Google's index with nothing telling them to stop - they
//    keep 200-ing forever without this. Collapsing here also defends against
//    any future call site that skips stripLocalePrefix() by mistake.
export async function onRequest(context) {
  const url = new URL(context.request.url);
  const fixedHost = url.hostname === 'niquit-web.pages.dev' ? 'niquit.app' : url.hostname;
  const fixedPath = url.pathname.replace(/\/{2,}/g, '/');
  if (fixedHost !== url.hostname || fixedPath !== url.pathname) {
    return Response.redirect(`https://${fixedHost}${fixedPath}${url.search}`, 301);
  }
  return context.next();
}
