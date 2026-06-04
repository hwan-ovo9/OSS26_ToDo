# FocusFlow

FocusFlow is a React + Vite productivity timer and task tracker. It stores tasks,
settings, and focus history in the browser with `localStorage`, so it can be
deployed as a static site on Netlify.

## Run Locally

**Prerequisites:** Node.js 20 or newer.

1. Install dependencies:

   ```bash
   npm install
   ```

2. Run the app:

   ```bash
   npm run dev
   ```

## Build

```bash
npm run build
```

The production build is written to `dist`.

## Deploy to Netlify

This repository includes `netlify.toml`, so Netlify can deploy it with:

- Build command: `npm run build`
- Publish directory: `dist`
- Node version: `22`

The redirect rule in `netlify.toml` serves `index.html` for all paths, which
keeps the app working on direct refreshes and shared URLs.
