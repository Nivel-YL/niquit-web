// niquit.app/get: one short profile link for every platform. The platform is read
// from the request: Instagram, Facebook and TikTok open links in their own in-app
// browsers, which name themselves in the user agent; YouTube passes itself as the
// referrer. Then it works exactly like /go/<platform> (store redirect + click count).
// ?s=<platform> overrides the guess. Anything unrecognised counts as "direct".
import { onRequest as go } from './go/[src].js';

function platform(request) {
  const s = new URL(request.url).searchParams.get('s');
  if (s) return s.toLowerCase();
  const ua = request.headers.get('user-agent') || '';
  if (/Instagram/i.test(ua)) return 'instagram';
  if (/FBAN|FBAV|FB_IAB|FBIOS/i.test(ua)) return 'facebook';
  if (/musical_ly|TikTok|BytedanceWebview|trill_/i.test(ua)) return 'tiktok';
  const ref = request.headers.get('referer') || '';
  if (/youtube\.com|youtu\.be/i.test(ref)) return 'youtube';
  return 'direct';
}

export function onRequest(context) {
  return go({ ...context, params: { src: platform(context.request) } });
}
