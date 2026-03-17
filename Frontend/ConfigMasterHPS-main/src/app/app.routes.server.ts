// app.routes.server.ts
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // All routes rendered client-side to avoid SSR bootstrap context issues
  // with browser-only providers (NgbModule, dialogs, etc.)
  { path: '**', renderMode: RenderMode.Client },
];
