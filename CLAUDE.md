# sircusmagazine.com: standing rules for site edits

Read this before changing any page. These rules keep Vercel Web Analytics accurate. They were introduced in PR #17 (October 13, 2026) and must survive every future edit, redesign or new page.

## 1. Every tracked page carries the analytics block

Pages that are tracked load Vercel Web Analytics with a plain script tag, and the self-exclusion block below must sit **immediately above** that tag. Never remove either one, never reorder them, and never add the tag without the block.

```html
<script>
/* Vercel Web Analytics: queue, plus a self-exclusion switch.
   Visit any page with ?va-disable=1 once per browser to stop counting your own visits; ?va-disable=0 turns counting back on. */
window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
(function () {
  try {
    var q = new URLSearchParams(location.search);
    if (q.has('va-disable')) {
      if (q.get('va-disable') === '0') localStorage.removeItem('va-disable');
      else localStorage.setItem('va-disable', '1');
    }
  } catch (err) {}
})();
window.va('beforeSend', function (event) {
  try { if (localStorage.getItem('va-disable')) return null; } catch (err) {}
  return event;
});
</script>
<script defer src="/_vercel/insights/script.js"></script>
```

Pages that carry it today (checked October 18, 2026): `index.html`, `about.html`, `journal.html`, `contact.html`, `issues/16-sunlit-reverie.html`, `stories/married-to-the-racist-that-is-me.html`, `editorials/darya-stone.html`, `editorials/erikka-gold.html`, `editorials/solenne-drive.html`.

**Every new page** (a new issue page, a new editorial, any new section) gets the full block above in its `<head>`. When a new page is built from an existing one as a template, confirm the block came across intact.

## 2. Story share pages forward the visit's source

The `story-*.html` files are share pages that redirect to `/?story=<slug>`, or, for a story that has its own page, to that page (`story-married-to-the-racist-that-is-me.html` forwards to `/stories/married-to-the-racist-that-is-me`). Their redirect script must pass along any `utm_` tags and, when there are none, tag the visit with the referring site. Without this, every shared-story visit shows up with no source, because the redirect makes sircusmagazine.com its own referrer.

The redirect line in each file has this form (only the slug in `u` changes):

```html
<script>(function(){var u='/?story=SLUG';try{var q=new URLSearchParams(location.search);if(!q.has('utm_source')&&document.referrer){var h=new URL(document.referrer).hostname;if(h&&h!==location.hostname){q.set('utm_source',h.replace(/^(www|m|l|lm)\./,''));q.set('utm_medium','referral');}}q.delete('story');var r=q.toString();if(r)u+='&'+r;}catch(e){}location.replace(u);})();</script>
```

**Every new story share page** uses this form, never a bare `location.replace('/?story=SLUG')`.

## 3. Redirects inside the site keep `utm_` tags

In `index.html`, the story loader sends stories that moved to the Issue 16 page onward through the `moved` map. That hop copies every `utm_` parameter onto the destination URL, placing it before any `#anchor`. Keep this behavior when editing the loader, and apply the same rule to any new redirect between pages: a visitor's campaign tags must arrive at the final page.

## 4. Don't break the measurement in other ways

- Don't add a second analytics script, a different analytics provider, or a cookie banner without Wil's approval.
- Don't strip the query string on page load before the analytics script has run. The existing `history.replaceState` that clears `?story=` happens only after the excerpt is closed, which is fine.
- Hidden review pages (anything noindex and unlinked) still carry the block, so Wil's own review visits are excluded rather than counted.

## 5. Check after any edit that touches page heads or redirects

1. Open `https://www.sircusmagazine.com/?va-disable=0` in a private window and confirm a request to `/_vercel/insights/view` fires.
2. Open the same page with `?va-disable=1` and confirm no such request fires.
3. Open `https://www.sircusmagazine.com/story-bald-by-design?utm_source=test` and confirm the address becomes `/?story=bald-by-design&utm_source=test` and the excerpt opens.

## Context

Wil marks each of his own browsers with `?va-disable=1`. Inbound links on his social bios, MagCloud descriptions and launch posts carry `utm_source`, `utm_medium` and `utm_campaign` tags, with the campaign named per issue (`issue16`, `issue17`). Visit counts are compared before and after each issue launch, so these rules decide whether those comparisons can be trusted.

This file is excluded from the live site by `.vercelignore`. Keep it out of the published build.
