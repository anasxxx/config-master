// app.routes.server.ts
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // Static Routes (Prerendered)
  { path: '', renderMode: RenderMode.Prerender }, // Root redirect (to /home)
  { path: 'login', renderMode: RenderMode.Prerender },
  { path: 'home', renderMode: RenderMode.Prerender },
  { path: 'dashboards', renderMode: RenderMode.Prerender },
  { path: 'banks', renderMode: RenderMode.Prerender },
  { path: 'activity', renderMode: RenderMode.Prerender },
  { path: 'addbank/step1', renderMode: RenderMode.Prerender },
  { path: 'addbank/step2', renderMode: RenderMode.Prerender },
  { path: 'addbank/step3', renderMode: RenderMode.Prerender },
  { path: 'side-bar-test', renderMode: RenderMode.Prerender },

  // Dynamic/Client-Side Routes
  { path: 'banks/details/:id', renderMode: RenderMode.Client },
  { path: 'banks/edit/:id', renderMode: RenderMode.Client },

  // Catch-All Wildcard (Client-Side)
  { path: '**', renderMode: RenderMode.Client },
];
