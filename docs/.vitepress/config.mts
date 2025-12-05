import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Fastpy',
  description: 'Production-ready FastAPI starter kit with 30+ CLI code generators, JWT authentication, SQLModel ORM, and built-in facades for rapid API development.',

  base: '/',

  cleanUrls: true,
  lastUpdated: true,
  sitemap: {
    hostname: 'https://vutia-ent.github.io/fastpy'
  },

  ignoreDeadLinks: [
    /^http:\/\/localhost/,
    /^http:\/\/test/
  ],

  head: [
    // Favicon
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16x16.png' }],
    ['link', { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' }],

    // Fonts
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap', rel: 'stylesheet' }],

    // Primary Meta Tags
    ['meta', { name: 'title', content: 'Fastpy - Production-ready FastAPI Starter Kit' }],
    ['meta', { name: 'description', content: 'Build FastAPI applications 10x faster with 30+ CLI generators, JWT authentication, SQLModel ORM, and built-in facades. The ultimate Python API starter kit.' }],
    ['meta', { name: 'keywords', content: 'FastAPI, Python, API, REST API, CLI, code generator, JWT, authentication, SQLModel, SQLAlchemy, Pydantic, starter kit, boilerplate, backend, web development' }],
    ['meta', { name: 'author', content: 'Vutia' }],
    ['meta', { name: 'robots', content: 'index, follow' }],
    ['meta', { name: 'language', content: 'English' }],
    ['meta', { name: 'revisit-after', content: '7 days' }],

    // Open Graph / Facebook
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:url', content: 'https://vutia-ent.github.io/fastpy/' }],
    ['meta', { property: 'og:title', content: 'Fastpy - Production-ready FastAPI Starter Kit' }],
    ['meta', { property: 'og:description', content: 'Build FastAPI applications 10x faster with 30+ CLI generators, JWT authentication, and built-in facades.' }],
    ['meta', { property: 'og:image', content: 'https://vutia-ent.github.io/fastpy/og-image.png' }],
    ['meta', { property: 'og:site_name', content: 'Fastpy' }],
    ['meta', { property: 'og:locale', content: 'en_US' }],

    // Twitter
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:url', content: 'https://vutia-ent.github.io/fastpy/' }],
    ['meta', { name: 'twitter:title', content: 'Fastpy - Production-ready FastAPI Starter Kit' }],
    ['meta', { name: 'twitter:description', content: 'Build FastAPI applications 10x faster with 30+ CLI generators, JWT authentication, and built-in facades.' }],
    ['meta', { name: 'twitter:image', content: 'https://vutia-ent.github.io/fastpy/og-image.png' }],
    ['meta', { name: 'twitter:creator', content: '@vutia' }],

    // Schema.org structured data
    ['script', { type: 'application/ld+json' }, JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'SoftwareApplication',
      name: 'Fastpy',
      applicationCategory: 'DeveloperApplication',
      operatingSystem: 'Cross-platform',
      description: 'Production-ready FastAPI starter kit with CLI code generators, JWT authentication, and built-in facades.',
      url: 'https://vutia-ent.github.io/fastpy/',
      author: {
        '@type': 'Organization',
        name: 'Vutia',
        url: 'https://github.com/vutia-ent'
      },
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'USD'
      },
      programmingLanguage: 'Python',
      softwareRequirements: 'Python 3.9+',
      license: 'https://opensource.org/licenses/MIT'
    })],
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
            { text: 'Tutorial: Build a Blog API', link: '/guide/tutorial' },
            { text: 'Configuration', link: '/guide/configuration' },
          ]
        },
        {
          text: 'Architecture',
          items: [
            { text: 'Project Structure', link: '/architecture/structure' },
            { text: 'Models & Concerns', link: '/architecture/models' },
            { text: 'Route Model Binding', link: '/architecture/binding' },
            { text: 'Patterns', link: '/architecture/patterns' },
            { text: 'Middleware', link: '/architecture/middleware' },
          ]
        },
        {
          text: 'Testing',
          items: [
            { text: 'Setup', link: '/testing/setup' },
            { text: 'Fixtures', link: '/testing/fixtures' },
            { text: 'Factories', link: '/testing/factories' },
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
            { text: 'Tutorial: Build a Blog API', link: '/guide/tutorial' },
            { text: 'Configuration', link: '/guide/configuration' },
          ]
        },
        {
          text: 'Architecture',
          items: [
            { text: 'Project Structure', link: '/architecture/structure' },
            { text: 'Models & Concerns', link: '/architecture/models' },
            { text: 'Route Model Binding', link: '/architecture/binding' },
            { text: 'Patterns', link: '/architecture/patterns' },
            { text: 'Middleware', link: '/architecture/middleware' },
          ]
        },
        {
          text: 'Testing',
          items: [
            { text: 'Setup', link: '/testing/setup' },
            { text: 'Fixtures', link: '/testing/fixtures' },
            { text: 'Factories', link: '/testing/factories' },
          ]
        }
      ],
      '/testing/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/guide/introduction' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Quick Start', link: '/guide/quickstart' },
            { text: 'Tutorial: Build a Blog API', link: '/guide/tutorial' },
            { text: 'Configuration', link: '/guide/configuration' },
          ]
        },
        {
          text: 'Architecture',
          items: [
            { text: 'Project Structure', link: '/architecture/structure' },
            { text: 'Models & Concerns', link: '/architecture/models' },
            { text: 'Route Model Binding', link: '/architecture/binding' },
            { text: 'Patterns', link: '/architecture/patterns' },
            { text: 'Middleware', link: '/architecture/middleware' },
          ]
        },
        {
          text: 'Testing',
          items: [
            { text: 'Setup', link: '/testing/setup' },
            { text: 'Fixtures', link: '/testing/fixtures' },
            { text: 'Factories', link: '/testing/factories' },
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
          text: 'Deployment',
          items: [
            { text: 'Production', link: '/deployment/production' },
            { text: 'Docker', link: '/deployment/docker' },
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
      '/deployment/': [
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
          text: 'Deployment',
          items: [
            { text: 'Production', link: '/deployment/production' },
            { text: 'Docker', link: '/deployment/docker' },
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
          text: 'Deployment',
          items: [
            { text: 'Production', link: '/deployment/production' },
            { text: 'Docker', link: '/deployment/docker' },
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
      '/examples/': [
        {
          text: 'Examples',
          items: [
            { text: 'Blog System', link: '/examples/blog' },
            { text: 'E-commerce', link: '/examples/ecommerce' },
            { text: 'API Service', link: '/examples/api-service' },
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
