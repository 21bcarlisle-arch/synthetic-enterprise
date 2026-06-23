# Standard Website Setup — Best Practices

## Context

poesys.net is now live on Cloudflare Pages. Several standard website
best practices are missing. Implement all of these as a single setup
task.

## DNS and Domain

1. **www redirect** — add www.poesys.net as a custom domain in
   Cloudflare Pages. Add a CNAME record in Cloudflare DNS:
   - Name: www
   - Target: poesys-net.pages.dev
   - Proxied: yes
   Both www.poesys.net and poesys.net should serve the same content.

2. **HTTP to HTTPS redirect** — ensure all HTTP traffic redirects to
   HTTPS automatically. Cloudflare handles this via SSL/TLS settings —
   enable "Always Use HTTPS" in Cloudflare dashboard → poesys.net →
   SSL/TLS → Edge Certificates.

3. **Root to www (or www to root) canonical redirect** — pick one as
   canonical (recommend root poesys.net) and redirect the other to it.
   Prevents duplicate content and split traffic.

## HTML and SEO basics

4. **Correct meta tags** in site/index.html:
   - `<title>Poesys — Synthetic Enterprise Dashboard</title>`
   - `<meta name="description" content="Live dashboard for the
     Synthetic Enterprise autonomous energy simulation">`
   - `<meta name="robots" content="noindex, nofollow">` — this is
     an internal tool, don't let search engines index it
   - `<link rel="canonical" href="https://poesys.net/">`
   - Open Graph tags for when the URL is shared:
     `<meta property="og:title" content="Poesys Dashboard">`
     `<meta property="og:url" content="https://poesys.net">`

5. **Favicon** — add a simple favicon.ico to site/. Without it every
   browser makes a 404 request on every page load. A simple green
   square on black (matching the terminal aesthetic) is fine.

6. **robots.txt** — already exists but confirm it allows all access:
   ```
   User-agent: *
   Allow: /
   ```
   Since we have noindex meta tags, crawlers won't index the content
   even if they can access it.

## Performance and reliability

7. **Cache-control headers** — add a _headers file to site/ so
   Cloudflare Pages serves correct cache headers:
   ```
   /*
     Cache-Control: no-cache, must-revalidate
   ```
   This prevents the stale DNS/cache issues Rich has been experiencing.
   The dashboard should always show fresh data.

8. **404 page** — add site/404.html with a simple "Page not found —
   go to dashboard" message linking back to the root. Without it
   Cloudflare serves a generic error page.

9. **Security headers** — add to _headers file:
   ```
   /*
     X-Frame-Options: DENY
     X-Content-Type-Options: nosniff
     Referrer-Policy: no-referrer
   ```
   Basic hardening — prevents the dashboard being embedded in iframes
   and protects against MIME sniffing.

## Mobile experience

10. **Viewport meta tag** — already present, confirm it's correct:
    `<meta name="viewport" content="width=device-width, initial-scale=1.0">`

11. **Touch icon** — add apple-touch-icon.png to site/ so when Rich
    adds poesys.net to his phone home screen it shows a proper icon
    rather than a screenshot.

## Verification

After implementing, verify:
- https://poesys.net loads correctly
- https://www.poesys.net loads and redirects to https://poesys.net
- http://poesys.net redirects to https://poesys.net
- Favicon appears in browser tab
- No 404 on favicon.ico request
- Cache-control headers present (check via browser dev tools)

## NTFY on completion

1. "Website setup complete. www.poesys.net live."
2. "Checklist: [list each item as done/skipped with reason]"
