# pizza-clock/webui

## Prerequisites

- Node.js v22.13

## Init

```sh
# Install dependencies
$ npm ci

# Start development server
$ npm run dev
```

## Build

```sh
$ npm run build
```

- Environment variables
  - `ASTRO_SITE`: Inject `astro.config.mjs:site`. See https://astro.build/config .
  - `ASTRO_BASE`: Inject `astro.config.mjs:base`
