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
const SOURCES = ['tiktok', 'instagram', 'youtube', 'facebook', 'direct'];
// The site's PostHog project (same public key as src/layouts/Base.astro).
const POSTHOG_KEY = 'phc_pwpnKbZ6ojRVeyV7QkuQQn6RhediJQhyEAjTZHTX7pPR';

const BOT_UA = /bot|crawl|spider|preview|facebookexternalhit|embedly|slurp|headless|python|curl|wget|go-http|okhttp/i;
const DATACENTRE = /facebook|meta platforms|google|amazon|aws|microsoft|azure|bytedance|tiktok|tencent|alibaba|huawei cloud|baidu|digitalocean|ovh|hetzner|linode|oracle|leaseweb|contabo|vultr|scaleway|choopa|m247|datacamp|zscaler/i;
// Not listed on purpose: Apple, Akamai, Cloudflare, Fastly carry iCloud Private Relay, i.e. real iPhone users.

// One anonymous event per request, sent from the server: no cookie, no person
// profile, no IP (the request comes from Cloudflare); country and network from Cloudflare.
// Clicks per platform are the number we read; the stores only show installs
// in their own consoles (Apple only for users who share analytics).
function countClick(waitUntil, props) {
  const body = JSON.stringify({
    api_key: POSTHOG_KEY,
    event: 'go_link_click',
    distinct_id: crypto.randomUUID(),
    properties: { ...props, $process_person_profile: false, $geoip_disable: true },
  });
  waitUntil(fetch('https://eu.i.posthog.com/i/v0/e/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body }).catch(() => {}));
}

export function onRequest({ request, params, waitUntil }) {
  const url = new URL(request.url);
  const src = String(params.src || '').toLowerCase();
  const source = SOURCES.includes(src) ? src : 'social';
  // Apple caps ct at 40 characters; "instagram_" + 29 stays under it.
  const tag = (url.searchParams.get('c') || '').toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 29);
  const campaign = tag ? `${source}_${tag}` : source;
  const utm = `utm_source=${source}&utm_medium=social&utm_campaign=${campaign}`;
  const ua = request.headers.get('user-agent') || '';

  const device = /iPhone|iPad|iPod/i.test(ua) ? 'ios' : /Android/i.test(ua) ? 'android' : 'other';

  let target;
  if (device === 'ios') target = `${APPLE}?pt=${APPLE_PROVIDER}&ct=${campaign}&mt=8`;
  else if (device === 'android') target = `${GOOGLE}&referrer=${encodeURIComponent(utm)}`;
  else target = `https://niquit.app/?${utm}`;

  // Every request is counted, flagged when it is not a person: link previews, and the
  // checks the platforms run on a new profile link. Those pose as iPhones from data
  // centres (Meta, ByteDance, Google...), so the network says more than the user agent.
  // The dashboard counts likely_bot = false only.
  const cf = request.cf || {};
  const org = String(cf.asOrganization || '');
  const likelyBot = request.method !== 'GET' || BOT_UA.test(ua) || DATACENTRE.test(org);
  countClick(waitUntil, { source, campaign, device, country: cf.country || null, as_org: org || null, asn: cf.asn || null, likely_bot: likelyBot, ua: ua.slice(0, 200) });

  return new Response(null, {
    status: 302,
    headers: { Location: target, 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' },
  });
}
