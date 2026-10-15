// Profile links for the short-video accounts: niquit.app/go/tiktok, /go/instagram,
// /go/youtube, /go/facebook. Optional ?c=<video> tags one video (a YouTube
// description link, say): niquit.app/go/youtube?c=day03.
// Same mechanics as functions/r.js: each phone goes straight to its store with a
// campaign tag, so installs per platform show up in App Store Connect (App
// Analytics > Sources > Campaigns) and Play Console (acquisition by utm_source
// and utm_campaign). Anything else gets the home page.
const APPLE = 'https://apps.apple.com/app/id6781069151';
const GOOGLE = 'https://play.google.com/store/apps/details?id=com.niquit.app';
// App Store Connect provider id (pt) of Nivexon OÜ, required for campaign links.
const APPLE_PROVIDER = '129049845';
const SOURCES = ['tiktok', 'instagram', 'youtube', 'facebook'];

export function onRequest({ request, params }) {
  const url = new URL(request.url);
  const src = String(params.src || '').toLowerCase();
  const source = SOURCES.includes(src) ? src : 'social';
  // Apple caps ct at 40 characters; "instagram_" + 29 stays under it.
  const tag = (url.searchParams.get('c') || '').toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 29);
  const campaign = tag ? `${source}_${tag}` : source;
  const utm = `utm_source=${source}&utm_medium=social&utm_campaign=${campaign}`;
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
