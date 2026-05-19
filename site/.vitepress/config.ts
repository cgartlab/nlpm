import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import footnote from 'markdown-it-footnote'

export default withMermaid(defineConfig({
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

  // Markdown extensions:
  //   - markdown-it-footnote: GFM-ish footnote syntax (`text[^1]`,
  //     `[^1]: definition` block at end of file).
  // Mermaid support is added by the withMermaid wrapper below.
  markdown: {
    config: (md) => {
      md.use(footnote)
    },
  },

  // Mermaid plugin config — uses dynamic import so SSR builds work and the
  // mermaid runtime is only loaded on pages that actually contain diagrams.
  mermaid: {
    // mermaid runtime options; defaults are fine, but pick a theme that
    // adapts to VitePress light/dark mode.
    theme: 'default',
  },
  mermaidPlugin: {
    class: 'mermaid-diagram',
  },

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
      { text: 'How it works', link: '/how-it-works' },
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
}))
