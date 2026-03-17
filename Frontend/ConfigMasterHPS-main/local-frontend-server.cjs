const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const browserDir = path.join(__dirname, 'dist', 'config-master', 'browser');
const indexPath = path.join(browserDir, 'index.csr.html');

let cachedIndexHtml = null;

function getIndexHtml() {
  if (!cachedIndexHtml) {
    let html = fs.readFileSync(indexPath, 'utf-8');
    // For local dev, serve app at root instead of /config-master/
    html = html.replace('<base href=\"/config-master/\">', '<base href=\"/\">');
    cachedIndexHtml = html;
  }
  return cachedIndexHtml;
}

// Serve static assets from browser build at root
app.use(express.static(browserDir, {
  maxAge: '1d',
  index: false,
}));

// Fallback to index for client-side routes
app.get('*', (_req, res) => {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.send(getIndexHtml());
});

const port = process.env.PORT || 4000;
app.listen(port, () => {
  console.log(`Local frontend server listening on http://localhost:${port}`);
});

