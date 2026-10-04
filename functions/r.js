// Short link for Reddit. niquit.app/r for DMs, niquit.app/r?c=stopsmoking as
// the target of a masked link ([niquit.app](...)) in posts and comments.
// Sends each phone straight to its store with a campaign tag, so installs per
// post show up in App Store Connect (App Analytics > Sources > Campaigns) and
// Play Console (acquisition by utm_campaign). Anything else gets the home page.
// A server-side redirect, not a page: no extra screen, and it works inside
// the Reddit app's own browser.
const APPLE = 'https://apps.apple.com/app/id6781069151';
const GOOGLE = 'https://play.google.com/store/apps/details?id=com.niquit.app';
// App Store Connect provider id (pt) of Nivexon OÜ, required for campaign links.
const APPLE_PROVIDER = '129049845';

export function onRequest({ request }) {
  const url = new URL(request.url);
  // Apple caps ct at 40 characters; "reddit_" + 30 stays under it.
  const tag = (url.searchParams.get('c') || '').toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 30);
  const campaign = tag ? `reddit_${tag}` : 'reddit';
  const utm = `utm_source=reddit&utm_medium=social&utm_campaign=${campaign}`;
  const ua = request.headers.get('user-agent') || '';

  let target;
  if (/iPhone|iPad|iPod/i.test(ua)) target = `${APPLE}?pt=${APPLE_PROVIDER}&ct=${campaign}&mt=8`;
  else if (/Android/i.test(ua)) target = `${GOOGLE}&referrer=${encodeURIComponent(utm)}`;
  else target = `https://niquit.app/?${utm}`;

  return new Response(null, {
    status: 302,
    headers: { Location: target, 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' },
  });
}
