// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://vutia-ent.github.io',
  base: '/fastpy',
  integrations: [
    starlight({
      title: 'Fastpy',
      description: 'Production-ready FastAPI starter with FastCLI code generator',
      logo: {
        light: './src/assets/logo-light.svg',
        dark: './src/assets/logo-dark.svg',
        replacesTitle: false,
      },
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/vutia-ent/fastpy' },
        { icon: 'x.com', label: 'Twitter', href: 'https://twitter.com/vutia' },
      ],
      head: [
        // Google Fonts - Inter
        {
          tag: 'link',
          attrs: { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        },
        {
          tag: 'link',
          attrs: { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true },
        },
        {
          tag: 'link',
          attrs: {
            rel: 'stylesheet',
            href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap',
          },
        },
        // Open Graph
        {
          tag: 'meta',
          attrs: { property: 'og:image', content: 'https://vutia-ent.github.io/fastpy/og-image.png' },
        },
        {
          tag: 'meta',
          attrs: { property: 'og:type', content: 'website' },
        },
      ],
      customCss: ['./src/styles/custom.css'],
      // Improved color theme
      components: {
        // You can override components here if needed
      },
      sidebar: [
        {
          label: 'Getting Started',
          items: [
            { label: 'Introduction', slug: 'getting-started/introduction' },
            { label: 'Installation', slug: 'getting-started/installation' },
            { label: 'Quick Start', slug: 'getting-started/quickstart' },
            { label: 'Configuration', slug: 'getting-started/configuration' },
          ],
        },
        {
          label: 'CLI Commands',
          items: [
            { label: 'Overview', slug: 'commands/overview' },
            { label: 'Server Commands', slug: 'commands/server' },
            { label: 'Database Commands', slug: 'commands/database' },
            { label: 'Make Commands', slug: 'commands/make' },
            { label: 'AI Integration', slug: 'commands/ai' },
          ],
        },
        {
          label: 'Field Types',
          items: [
            { label: 'Overview', slug: 'fields/overview' },
            { label: 'Basic Types', slug: 'fields/basic' },
            { label: 'Advanced Types', slug: 'fields/advanced' },
            { label: 'Validation Rules', slug: 'fields/validation' },
          ],
        },
        {
          label: 'Architecture',
          items: [
            { label: 'Project Structure', slug: 'architecture/structure' },
            { label: 'Patterns', slug: 'architecture/patterns' },
            { label: 'Middleware', slug: 'architecture/middleware' },
          ],
        },
        {
          label: 'API Reference',
          items: [
            { label: 'Authentication', slug: 'api/authentication' },
            { label: 'Responses', slug: 'api/responses' },
            { label: 'Exceptions', slug: 'api/exceptions' },
            { label: 'Pagination', slug: 'api/pagination' },
          ],
        },
        {
          label: 'Testing',
          items: [
            { label: 'Setup', slug: 'testing/setup' },
            { label: 'Fixtures', slug: 'testing/fixtures' },
            { label: 'Factories', slug: 'testing/factories' },
          ],
        },
        {
          label: 'Deployment',
          items: [
            { label: 'Production', slug: 'deployment/production' },
            { label: 'Docker', slug: 'deployment/docker' },
          ],
        },
        {
          label: 'Examples',
          items: [
            { label: 'Blog System', slug: 'examples/blog' },
            { label: 'E-commerce', slug: 'examples/ecommerce' },
            { label: 'API Service', slug: 'examples/api-service' },
          ],
        },
      ],
      editLink: {
        baseUrl: 'https://github.com/vutia-ent/fastpy/edit/main/docs/',
      },
      lastUpdated: true,
      tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },
      pagination: true,
      favicon: '/favicon.svg',
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
