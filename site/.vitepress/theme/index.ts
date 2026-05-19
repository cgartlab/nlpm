// Custom VitePress theme — extends the default theme and registers
// report-rendering Vue components globally so they can be used inside
// any Markdown page via <DashboardPanels :data="..." />.
import DefaultTheme from 'vitepress/theme'
import DashboardPanels from './components/DashboardPanels.vue'
import type { Theme } from 'vitepress'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('DashboardPanels', DashboardPanels)
  },
} satisfies Theme
