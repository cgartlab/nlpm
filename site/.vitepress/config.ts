import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'NLPM',
  description:
    'Natural Language Programming Manager — scores, audits, and disciplines NL artifacts in Claude Code plugins.',
  cleanUrls: true,
  lastUpdated: true,
  // Where to write the build output and where static passthrough lives.
  outDir: '.vitepress/dist',
  // public/ is the standard VitePress static-passthrough directory; the
  // build pipeline copies auditor/reports/* into site/public/ before
  // running `pnpm build`.

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'NLPM — Natural Language Programming Manager' }],
    ['meta', { property: 'og:url', content: 'https://nlpm.com/' }],
    ['meta', {
      property: 'og:description',
      content:
        'A Claude Code plugin that scores, audits, and disciplines natural-language artifacts. ' +
        'Cross-repo dashboards and per-repo audit reports for 200+ Claude Code plugins.',
    }],
  ],

  themeConfig: {
    siteTitle: 'NLPM',

    nav: [
      { text: 'Home', link: '/' },
      { text: 'Install', link: '/install' },
      {
        text: 'Audit data',
        items: [
          { text: 'Dashboard', link: '/dashboard.html' },
          { text: 'Sample repo report', link: '/SuperClaude-Org-SuperClaude_Framework.html' },
        ],
      },
      { text: 'Reference', link: '/reference/' },
      { text: 'GitHub', link: 'https://github.com/xiaolai/nlpm-for-claude' },
    ],

    sidebar: {
      '/reference/': [
        {
          text: 'Framework reference',
          items: [
            { text: 'Overview', link: '/reference/' },
            { text: 'Rules (R01–R51)', link: '/reference/rules' },
            { text: 'Vocabulary principles', link: '/reference/principles' },
            { text: 'Vocabulary concepts', link: '/reference/vocabulary' },
            { text: 'Scoring & severity', link: '/reference/scoring' },
            { text: 'Artifact types', link: '/reference/artifact-types' },
            { text: 'Drift criteria', link: '/reference/drift' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/xiaolai/nlpm-for-claude' },
    ],

    search: {
      provider: 'local',
    },

    footer: {
      message: 'MIT-licensed Claude Code plugin.',
      copyright: '© xiaolai · Generated from canonical SKILL.md sources',
    },

    editLink: {
      pattern: 'https://github.com/xiaolai/nlpm-for-claude/edit/main/site/:path',
      text: 'Edit this page on GitHub',
    },

    outline: { level: [2, 3], label: 'On this page' },
  },
})
