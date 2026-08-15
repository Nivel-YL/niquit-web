# Ideas — niquit-web

Feature ideas for the site, not yet scheduled. Not a sprint backlog like
`BLOG_TOPIC_BACKLOG.md` (that one is articles with a defined pipeline) -
just things worth remembering when there's room to build them.

## Standalone shareable calculator/tool

**Why:** the blog covers the same topics as prose, but a self-contained
interactive tool is what people actually forward to a friend or link to
from a forum/Reddit thread, instead of reading an article and closing the
tab. That's a real backlink lever - discussed 2026-08-15: content volume
alone doesn't move ranking much without external links pointing back to
the site, and this is one of the more realistic ways to earn them
organically instead of through outreach.

**Direction, not a spec:**
- Immediate, personal, shareable result - e.g. money saved quitting
  (cigarettes/vapes/pouches, by frequency and local price), or a
  nicotine-withdrawal timeline personalized to how long/how much someone
  used.
- Needs its own clean URL, works standalone without requiring the app,
  and should have an obvious "share this" moment - a result worth
  screenshotting or sending, not just a filled-in form.
- 5 languages, same as the rest of the site.

**Not decided yet:** exact concept, whether it lives at `/tools/...` as
its own thing or also gets a linkable blog treatment pointing at it, how
it's built (probably a plain Astro island / vanilla JS, no reason for a
backend for something this self-contained).
