// Simple service worker for showing notifications
self.addEventListener('message', (event) => {
  const data = event.data || {}
  if (data.type === 'SHOW_NOTIFICATION' && data.title) {
    self.registration.showNotification(data.title, {
      body: data.body || '',
      icon: data.icon || undefined,
      tag: data.tag || undefined
    })
  }
})

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window" }).then(clientList => {
      for (const client of clientList) {
        if ('focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow('/');
    })
  );
});
