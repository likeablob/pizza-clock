// @ts-check
import react from '@astrojs/react'
import tailwind from '@astrojs/tailwind'
import { defineConfig } from 'astro/config'

// https://astro.build/config
export default defineConfig({
  site: process.env.ASTRO_SITE,
  base: process.env.ASTRO_BASE,
  integrations: [
    react(),
    tailwind({
      applyBaseStyles: false,
    }),
  ],
})
