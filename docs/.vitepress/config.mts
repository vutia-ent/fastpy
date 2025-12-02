import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Fastpy',
  description: 'Production-ready FastAPI starter with FastCLI code generator',

  base: '/',

  cleanUrls: true,
  lastUpdated: true,

  ignoreDeadLinks: [
    /^http:\/\/localhost/,
    /^http:\/\/test/
  ],

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap', rel: 'stylesheet' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'Fastpy - Production-ready FastAPI Starter' }],
    ['meta', { property: 'og:description', content: 'Build FastAPI applications faster with FastCLI code generator, JWT auth, and battle-tested patterns.' }],
    ['meta', { property: 'og:image', content: 'https://vutia-ent.github.io/fastpy/og-image.png' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:title', content: 'Fastpy - Production-ready FastAPI Starter' }],
    ['meta', { name: 'twitter:description', content: 'Build FastAPI applications faster with FastCLI code generator, JWT auth, and battle-tested patterns.' }],
  ],

  appearance: 'dark',

  markdown: {
    lineNumbers: true,
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    }
  },

  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'Fastpy',

    nav: [
      { text: 'Guide', link: '/guide/introduction' },
      { text: 'CLI Commands', link: '/commands/overview' },
      { text: 'Libs', link: '/libs/overview' },
      { text: 'API Reference', link: '/api/authentication' },
      { text: 'Examples', link: '/examples/blog' },
      {
        text: 'v1.0.0',
        items: [
          { text: 'Changelog', link: 'https://github.com/vutia-ent/fastpy/releases' },
          { text: 'Contributing', link: 'https://github.com/vutia-ent/fastpy/blob/main/CONTRIBUTING.md' },
        ]
      }
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/guide/introduction' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Quick Start', link: '/guide/quickstart' },
            { text: 'Configuration', link: '/guide/configuration' },
          ]
        },
        {
          text: 'Architecture',
          items: [
            { text: 'Project Structure', link: '/architecture/structure' },
            { text: 'Patterns', link: '/architecture/patterns' },
            { text: 'Middleware', link: '/architecture/middleware' },
          ]
        }
      ],
      '/architecture/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/guide/introduction' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Quick Start', link: '/guide/quickstart' },
            { text: 'Configuration', link: '/guide/configuration' },
          ]
        },
        {
          text: 'Architecture',
          items: [
            { text: 'Project Structure', link: '/architecture/structure' },
            { text: 'Patterns', link: '/architecture/patterns' },
            { text: 'Middleware', link: '/architecture/middleware' },
          ]
        }
      ],
      '/commands/': [
        {
          text: 'CLI Commands',
          items: [
            { text: 'Overview', link: '/commands/overview' },
            { text: 'Server Commands', link: '/commands/server' },
            { text: 'Database Commands', link: '/commands/database' },
            { text: 'Make Commands', link: '/commands/make' },
            { text: 'AI Commands', link: '/commands/ai' },
          ]
        },
        {
          text: 'Field Types',
          items: [
            { text: 'Overview', link: '/fields/overview' },
            { text: 'Basic Types', link: '/fields/basic' },
            { text: 'Advanced Types', link: '/fields/advanced' },
            { text: 'Validation Rules', link: '/fields/validation' },
          ]
        }
      ],
      '/api/': [
        {
          text: 'API Reference',
          items: [
            { text: 'Swagger UI / OpenAPI', link: '/api/swagger' },
            { text: 'Authentication', link: '/api/authentication' },
            { text: 'Responses', link: '/api/responses' },
            { text: 'Exceptions', link: '/api/exceptions' },
            { text: 'Pagination', link: '/api/pagination' },
          ]
        }
      ],
      '/libs/': [
        {
          text: 'Fastpy Libs',
          items: [
            { text: 'Overview', link: '/libs/overview' },
            { text: 'Http', link: '/libs/http' },
            { text: 'Cache', link: '/libs/cache' },
            { text: 'Mail', link: '/libs/mail' },
            { text: 'Storage', link: '/libs/storage' },
            { text: 'Queue', link: '/libs/queue' },
            { text: 'Events', link: '/libs/events' },
            { text: 'Hash', link: '/libs/hashing' },
            { text: 'Crypt', link: '/libs/encryption' },
            { text: 'Notify', link: '/libs/notifications' },
          ]
        }
      ],
      '/testing/': [
        {
          text: 'Testing',
          items: [
            { text: 'Setup', link: '/testing/setup' },
            { text: 'Fixtures', link: '/testing/fixtures' },
            { text: 'Factories', link: '/testing/factories' },
          ]
        }
      ],
      '/deployment/': [
        {
          text: 'Deployment',
          items: [
            { text: 'Production', link: '/deployment/production' },
            { text: 'Docker', link: '/deployment/docker' },
          ]
        }
      ],
      '/examples/': [
        {
          text: 'Examples',
          items: [
            { text: 'Blog System', link: '/examples/blog' },
            { text: 'E-commerce', link: '/examples/ecommerce' },
            { text: 'API Service', link: '/examples/api-service' },
          ]
        }
      ],
      '/fields/': [
        {
          text: 'CLI Commands',
          items: [
            { text: 'Overview', link: '/commands/overview' },
            { text: 'Server Commands', link: '/commands/server' },
            { text: 'Database Commands', link: '/commands/database' },
            { text: 'Make Commands', link: '/commands/make' },
            { text: 'AI Commands', link: '/commands/ai' },
          ]
        },
        {
          text: 'Field Types',
          items: [
            { text: 'Overview', link: '/fields/overview' },
            { text: 'Basic Types', link: '/fields/basic' },
            { text: 'Advanced Types', link: '/fields/advanced' },
            { text: 'Validation Rules', link: '/fields/validation' },
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vutia-ent/fastpy' },
      { icon: 'x', link: 'https://twitter.com/vutia' }
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present Vutia'
    },

    editLink: {
      pattern: 'https://github.com/vutia-ent/fastpy/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },

    search: {
      provider: 'local',
      options: {
        detailedView: true,
        miniSearch: {
          searchOptions: {
            fuzzy: 0.2,
            prefix: true,
            boost: {
              title: 4,
              text: 2,
              titles: 1
            }
          }
        }
      }
    },

    outline: {
      level: [2, 3],
      label: 'On this page'
    },

    lastUpdated: {
      text: 'Updated at',
      formatOptions: {
        dateStyle: 'medium',
        timeStyle: 'short'
      }
    },

    docFooter: {
      prev: 'Previous',
      next: 'Next'
    },

    returnToTopLabel: 'Back to top',
    sidebarMenuLabel: 'Menu',
    darkModeSwitchLabel: 'Theme',
    lightModeSwitchTitle: 'Switch to light mode',
    darkModeSwitchTitle: 'Switch to dark mode'
  }
})
