// ...new file...
const CACHE_NAME = 'models-v1';
const MODEL_URLS = [
  '/static/models_3d/car/scene.gltf',
  '/static/models_3d/wrench/scene.gltf',
  '/static/models_3d/user/scene.gltf',
  '/static/models_3d/order/scene.gltf',
  '/static/models_3d/engine/scene.gltf',
  '/static/models_3d/dashboard/scene.gltf',
  '/static/models_3d/crane/scene.gltf',
  '/static/models_3d/worker/scene.gltf'
];

// precache models on install
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(MODEL_URLS))
      .then(() => self.skipWaiting())
  );
});

// activate - clean old caches if needed
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// intercept fetch for model urls and respond from cache (fallback to network)
self.addEventListener('fetch', event => {
  try {
    const reqUrl = new URL(event.request.url);
    if (MODEL_URLS.includes(reqUrl.pathname)) {
      event.respondWith(
        caches.match(event.request).then(cached => cached || fetch(event.request).then(resp => {
          // update cache in background
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, resp.clone()));
          return resp;
        }))
      );
    }
  } catch (e) {
    // ignore non-HTTP requests.
  }
});