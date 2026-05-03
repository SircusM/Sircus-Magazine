/*
 * SIRCUS — Service Worker
 * Strategy: cache-first for static assets, network-first for HTML pages.
 * Safe versioned cache — old caches are purged on activate.
 * Do not modify without updating CACHE_VERSION.
 */

var CACHE_VERSION = 'sircus-v1';

var STATIC_SHELL = [
  '/',
  '/index.html',
  '/contact.html',
  '/site.webmanifest',
  '/favicon.svg',
  '/favicon.ico',
  '/favicon-96x96.png',
  '/apple-touch-icon.png',
  '/android-chrome-192x192.png',
  '/android-chrome-512x512.png'
];

/* ── INSTALL — pre-cache the site shell ── */
self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(function (cache) {
      return cache.addAll(STATIC_SHELL);
    }).then(function () {
      /* Skip waiting so the new SW activates immediately on next navigation */
      return self.skipWaiting();
    })
  );
});

/* ── ACTIVATE — purge stale caches ── */
self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (key) {
          return key !== CACHE_VERSION;
        }).map(function (key) {
          return caches.delete(key);
        })
      );
    }).then(function () {
      /* Take control of all open clients without a page reload */
      return self.clients.claim();
    })
  );
});

/* ── FETCH — route by content type ── */
self.addEventListener('fetch', function (event) {
  var request = event.request;
  var url = new URL(request.url);

  /* Only handle same-origin requests */
  if (url.origin !== self.location.origin) return;

  /* Ignore non-GET requests (forms, API calls) */
  if (request.method !== 'GET') return;

  /* HTML pages — network-first so content updates reach the user */
  if (request.headers.get('Accept') && request.headers.get('Accept').indexOf('text/html') !== -1) {
    event.respondWith(
      fetch(request).then(function (networkResponse) {
        /* Update the cache with the fresh response */
        var clone = networkResponse.clone();
        caches.open(CACHE_VERSION).then(function (cache) {
          cache.put(request, clone);
        });
        return networkResponse;
      }).catch(function () {
        /* Network unavailable — serve cached HTML */
        return caches.match(request).then(function (cached) {
          return cached || caches.match('/index.html');
        });
      })
    );
    return;
  }

  /* Static assets (images, fonts, manifest, favicons) — cache-first */
  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) return cached;
      return fetch(request).then(function (networkResponse) {
        var clone = networkResponse.clone();
        caches.open(CACHE_VERSION).then(function (cache) {
          cache.put(request, clone);
        });
        return networkResponse;
      });
    })
  );
});
