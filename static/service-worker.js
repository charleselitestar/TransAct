const CACHE_NAME = "elite-docs-cache-v1";
const urlsToCache = [
  "/",
  "/static/images/2023.png", // Adjust the path based on your actual file structure
  // Add other URLs or assets you want to cache
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }

      const fetchRequest = event.request.clone();

      return fetch(fetchRequest).then((response) => {
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }

        const responseToCache = response.clone();

        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        // Notify the client that the connection is established
        clients.matchAll().then((clients) => {
          clients.forEach((client) => {
            client.postMessage({ connectionEstablished: true });
          });
        });

        return response;
      });
    })
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener("message", (event) => {
  if (event.data.action === "hideSplashScreen") {
    // Hide the splash screen when instructed by the main page
    self.registration.showNotification("EliteDoc's", {
      body: "Connection established. You are now offline-ready!",
      icon: "/static/images/notification-icon.png", // Adjust the path based on your actual file structure
    });
  }
});
