// Cloudflare Pages runs this on every request to the project, regardless of
// which attached domain received it. Its only job: redirect the platform's
// own niquit-web.pages.dev subdomain to the real site. That subdomain can't
// be turned off (every Pages project has one) and public/_redirects can't
// redirect it either - Cloudflare doesn't apply _redirects host rules to a
// project's own pages.dev domain or to its attached custom domains, so a
// rule living in that file for this exact purpose was silently inert before
// this Function replaced it (2026-08-15 investigation: niquit-web.pages.dev
// was fully live and crawlable, canonical tags pointed at niquit.app but
// Google doesn't always defer to a declared canonical over an actually-
// crawlable duplicate).
export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.hostname === 'niquit-web.pages.dev') {
    return Response.redirect(`https://niquit.app${url.pathname}${url.search}`, 301);
  }
  return context.next();
}
