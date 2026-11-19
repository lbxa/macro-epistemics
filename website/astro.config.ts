import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import icon from 'astro-icon';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: "https://epistemics.lbxa.net",

  // Research PDFs and video load only when requested, never on viewport entry.
  prefetch: false,

  vite: { plugins: [tailwindcss()] },

  integrations: [
    react(),
    mdx({
      remarkPlugins: [remarkMath],
      rehypePlugins: [rehypeKatex],
      syntaxHighlight: 'shiki',
      shikiConfig: {
        themes: { 
          light: "one-light",
          dark: "dark-plus",
        },
      }
    }), 
    icon({
      iconDir: "src/assets/icons",
    })
  ],
});
