<!--
  DashboardPanels.vue — renders the auditor cross-repo dashboard from
  DashboardData (see analysis/report-data-schema.md).

  Five panels, one per section in the schema:
    1. KPI tiles  (summary)
    2. Repo table (repo_rows) — sortable
    3. Rule distribution bar chart (rule_distribution) — pure CSS bars
       with rotated labels (matches the standalone dashboard's look)
    4. Cross-repo drift network (drift_network) — G6 force-directed
    5. Activity timeline (activity_timeline) — G6 multi-line
-->
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import { Graph } from '@antv/g6'

type RepoRow = {
  repo: string
  status?: string | null
  stars?: number | null
  score?: number | null
  security?: string | null
  total_findings: number
  high_findings: number
  vocab_drift_count: number
  vocab_drift_high?: number
}
type RuleDistEntry = { rule_id: string; total: number; repos_affected: number }
type DriftNode = { id: string; label: string; freq: number; repos: string[] }
type DriftEdge = { source: string; target: string; weight: number; repos: string[] }
type ActivityDay = { day: string; counts: Record<string, number> }

type DashboardData = {
  generated_at?: string
  since?: string | null
  summary: {
    total_repos: number
    total_findings: number
    high_findings: number
    total_advisories: number
    high_advisories: number
    repos_with_drift: number
    repos_blocked: number
  }
  repo_rows: RepoRow[]
  rule_distribution: RuleDistEntry[]
  drift_network: { nodes: DriftNode[]; edges: DriftEdge[] }
  activity_timeline: ActivityDay[]
}

const props = defineProps<{ data: DashboardData }>()
const d = computed(() => props.data)

// ----- KPIs -----
const tiles = computed(() => [
  { v: d.value.summary.total_repos, l: 'repos' },
  { v: d.value.summary.total_findings, l: 'findings' },
  { v: d.value.summary.total_advisories, l: 'advisories' },
  { v: d.value.summary.repos_with_drift, l: 'with drift' },
])

// ----- Repo table — sortable -----
const sortKey = ref<keyof RepoRow>('total_findings')
const sortDir = ref<'asc' | 'desc'>('desc')
const sortedRows = computed(() => {
  const rows = [...d.value.repo_rows]
  rows.sort((a, b) => {
    const av = a[sortKey.value]
    const bv = b[sortKey.value]
    if (typeof av === 'number' && typeof bv === 'number') {
      return sortDir.value === 'asc' ? av - bv : bv - av
    }
    const sa = String(av ?? '')
    const sb = String(bv ?? '')
    return sortDir.value === 'asc' ? sa.localeCompare(sb) : sb.localeCompare(sa)
  })
  return rows
})
function sortBy(k: keyof RepoRow) {
  if (sortKey.value === k) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else { sortKey.value = k; sortDir.value = 'desc' }
}
function slugFor(repo: string) { return repo.replace(/\//g, '-') }

// ----- Rule distribution bars -----
const rules = computed(() => d.value.rule_distribution || [])
const maxRuleTotal = computed(() => Math.max(1, ...rules.value.map((r) => r.total)))

// ----- Drift network — G6 -----
const driftEl = ref<HTMLDivElement | null>(null)
let driftGraph: Graph | null = null

// ----- Activity timeline — G6 -----
const activityEl = ref<HTMLDivElement | null>(null)
let activityGraph: Graph | null = null

const palette = ['#2b5fff', '#8b3fff', '#ff9d2b', '#2a8a3d', '#c63030']

onMounted(() => {
  if (driftEl.value && (d.value.drift_network?.nodes?.length ?? 0) > 0) {
    driftGraph = mountDriftGraph(driftEl.value, d.value.drift_network)
  }
  if (activityEl.value && (d.value.activity_timeline?.length ?? 0) >= 2) {
    activityGraph = mountActivityGraph(activityEl.value, d.value.activity_timeline)
  }
})
onBeforeUnmount(() => {
  driftGraph?.destroy()
  activityGraph?.destroy()
})

function mountDriftGraph(container: HTMLDivElement, net: { nodes: DriftNode[]; edges: DriftEdge[] }): Graph {
  const maxFreq = Math.max(1, ...net.nodes.map((n) => n.freq || 1))
  const maxWeight = Math.max(1, ...net.edges.map((e) => e.weight || 1))
  const graph = new Graph({
    container,
    data: {
      nodes: net.nodes.map((n) => ({
        id: n.id,
        data: { label: n.label, freq: n.freq, repos: n.repos },
        style: {
          size: 14 + 30 * Math.sqrt((n.freq || 1) / maxFreq),
          fill: n.freq >= 3 ? '#c63030' : n.freq >= 2 ? '#c47c00' : '#2b5fff',
          labelText: n.label,
          labelFontSize: 11,
          labelPosition: 'bottom',
        },
      })),
      edges: net.edges.map((e) => ({
        source: e.source,
        target: e.target,
        data: { weight: e.weight, repos: e.repos },
        style: {
          stroke: '#8888aa',
          lineWidth: 1 + 4 * ((e.weight || 1) / maxWeight),
          opacity: 0.4 + 0.6 * ((e.weight || 1) / maxWeight),
        },
      })),
    },
    node: { type: 'circle' },
    edge: { type: 'line' },
    layout: { type: 'd3-force', linkDistance: 70, nodeStrength: -180 },
    behaviors: ['zoom-canvas', 'drag-canvas', 'drag-element'],
    autoFit: 'view',
  })
  graph.render()
  return graph
}

function mountActivityGraph(container: HTMLDivElement, tl: ActivityDay[]): Graph {
  const totals: Record<string, number> = {}
  for (const day of tl) for (const [k, v] of Object.entries(day.counts || {})) totals[k] = (totals[k] || 0) + v
  const topEvents = Object.entries(totals).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([k]) => k)
  const W = 900, H = 240, margin = 40
  const days = tl.map((d) => d.day)
  const maxVal = Math.max(1, ...tl.flatMap((d) => topEvents.map((e) => d.counts?.[e] || 0)))
  const xStep = (W - 2 * margin) / Math.max(1, days.length - 1)
  const nodes: any[] = []
  const edges: any[] = []
  topEvents.forEach((ev, evIdx) => {
    tl.forEach((day, i) => {
      const id = `${ev}-${i}`
      const val = day.counts?.[ev] || 0
      nodes.push({
        id,
        data: { label: `${ev}: ${val}`, day: day.day },
        style: {
          x: margin + i * xStep,
          y: H - margin - (val / maxVal) * (H - 2 * margin),
          size: 4,
          fill: palette[evIdx],
        },
      })
      if (i > 0) {
        edges.push({
          source: `${ev}-${i - 1}`,
          target: id,
          style: { stroke: palette[evIdx], lineWidth: 1.5, opacity: 0.8 },
        })
      }
    })
  })
  const graph = new Graph({
    container,
    data: { nodes, edges },
    node: { type: 'circle' },
    edge: { type: 'line' },
    behaviors: ['zoom-canvas', 'drag-canvas'],
    autoFit: 'view',
  })
  graph.render()
  // Stash topEvents on the element for the legend below
  ;(container as any)._topEvents = topEvents.map((e, i) => ({ name: e, color: palette[i], total: totals[e] }))
  return graph
}

const activityLegend = computed<Array<{ name: string; color: string; total: number }>>(() => {
  const el = activityEl.value as any
  return el?._topEvents ?? []
})
</script>

<template>
  <div class="dash">
    <!-- KPI tiles -->
    <header class="dash-hdr">
      <h2 class="dash-h2">Cross-repo aggregate</h2>
      <p class="dash-meta">
        Generated {{ d.generated_at || '—' }} ·
        <span v-if="d.since">since {{ d.since }} · </span>
        <span class="muted">data source: <code>auditor/reports/dashboard.json</code></span>
      </p>
      <div class="kpis">
        <div v-for="t in tiles" :key="t.l" class="kpi">
          <div class="v">{{ t.v }}</div>
          <div class="l">{{ t.l }}</div>
        </div>
      </div>
    </header>

    <!-- Repos table -->
    <section class="panel">
      <h3>Audited repos</h3>
      <p class="hint">One row per repo. Click a column header to sort. The repo name links into the per-repo report.</p>
      <div class="table-wrap">
        <table class="repo-table">
          <thead>
            <tr>
              <th @click="sortBy('repo')" :class="{ active: sortKey === 'repo' }">Repo</th>
              <th @click="sortBy('status')" :class="{ active: sortKey === 'status' }">Status</th>
              <th @click="sortBy('stars')" :class="{ active: sortKey === 'stars' }">Stars</th>
              <th @click="sortBy('score')" :class="{ active: sortKey === 'score' }">Score</th>
              <th @click="sortBy('security')" :class="{ active: sortKey === 'security' }">Security</th>
              <th @click="sortBy('total_findings')" :class="{ active: sortKey === 'total_findings' }">Findings</th>
              <th @click="sortBy('high_findings')" :class="{ active: sortKey === 'high_findings' }">High</th>
              <th @click="sortBy('vocab_drift_count')" :class="{ active: sortKey === 'vocab_drift_count' }">Vocab drift</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in sortedRows" :key="r.repo">
              <td><a :href="`/${slugFor(r.repo)}.html`"><code>{{ r.repo }}</code></a></td>
              <td>{{ r.status ?? '—' }}</td>
              <td>{{ r.stars ?? '—' }}</td>
              <td>{{ r.score ?? '—' }}</td>
              <td :class="`security sec-${r.security ?? 'UNKNOWN'}`">{{ r.security ?? '—' }}</td>
              <td>{{ r.total_findings }}</td>
              <td>{{ r.high_findings }}</td>
              <td>
                {{ r.vocab_drift_count }}
                <span v-if="r.vocab_drift_high" class="muted">({{ r.vocab_drift_high }} high)</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Rule distribution -->
    <section class="panel">
      <h3>Rule distribution across all audits</h3>
      <p class="hint">Top rules by total occurrence. Labels read bottom-left → top-right.</p>
      <div v-if="rules.length === 0" class="empty">No findings logged yet.</div>
      <div v-else class="rule-bars">
        <div v-for="r in rules" :key="r.rule_id" class="rule-col">
          <div
            class="bar"
            :style="{ height: `${(r.total / maxRuleTotal) * 100}%` }"
            :title="`${r.rule_id}: ${r.total} occurrences across ${r.repos_affected} repos`"
          />
          <div class="rule-label">
            <a :href="`/reference/rules#${r.rule_id}`">{{ r.rule_id }}</a>
          </div>
        </div>
      </div>
      <table class="rule-detail">
        <thead><tr><th>Rule</th><th class="r">Occurrences</th><th class="r">Repos affected</th></tr></thead>
        <tbody>
          <tr v-for="r in rules" :key="r.rule_id">
            <td><a :href="`/reference/rules#${r.rule_id}`"><code>{{ r.rule_id }}</code></a></td>
            <td class="r">{{ r.total }}</td>
            <td class="r">{{ r.repos_affected }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Cross-repo drift network -->
    <section class="panel">
      <h3>Cross-repo vocabulary drift network</h3>
      <p class="hint">Term nodes; edges connect terms that co-cluster across repos. Hubs = terms drifting across the ecosystem.</p>
      <div ref="driftEl" class="g6-frame drift-frame">
        <div v-if="(d.drift_network?.nodes?.length ?? 0) === 0" class="empty inline">
          No vocab-drift advisories logged yet.
        </div>
      </div>
    </section>

    <!-- Activity timeline -->
    <section class="panel">
      <h3>Activity timeline</h3>
      <p class="hint">Daily event counts from <code>auditor/logs/events.jsonl</code>.</p>
      <div ref="activityEl" class="g6-frame">
        <div v-if="(d.activity_timeline?.length ?? 0) < 2" class="empty inline">
          Need at least 2 days of events to render a timeline.
        </div>
      </div>
      <div class="legend">
        <span v-for="ev in activityLegend" :key="ev.name" class="legend-item">
          <span class="dot" :style="{ background: ev.color }"></span>
          <code>{{ ev.name }}</code> ({{ ev.total }})
        </span>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dash { display: flex; flex-direction: column; gap: 24px; }
.dash-hdr h2 { margin: 0 0 4px; font-size: 18px; }
.dash-hdr .dash-meta { margin: 0; font-size: 12px; color: var(--vp-c-text-2); }
.muted { color: var(--vp-c-text-2); }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; margin-top: 16px; }
.kpi { padding: 10px 14px; background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-divider); border-radius: 6px; }
.kpi .v { font-size: 22px; font-weight: 700; }
.kpi .l { font-size: 11px; color: var(--vp-c-text-2); text-transform: uppercase; letter-spacing: 0.04em; }
.panel { padding: 16px; border: 1px solid var(--vp-c-divider); border-radius: 8px; background: var(--vp-c-bg-soft); }
.panel h3 { margin: 0 0 4px; font-size: 15px; font-weight: 600; }
.hint { margin: 0 0 12px; font-size: 12px; color: var(--vp-c-text-2); }
.empty { padding: 24px; color: var(--vp-c-text-2); text-align: center; }
.empty.inline { padding: 24px; }
.table-wrap { overflow-x: auto; }
.repo-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.repo-table th, .repo-table td { padding: 5px 8px; border-bottom: 1px solid var(--vp-c-divider); text-align: left; }
.repo-table th { background: var(--vp-c-bg); cursor: pointer; user-select: none; font-weight: 600; }
.repo-table th.active { color: var(--vp-c-brand-1); }
.repo-table a { color: inherit; text-decoration: none; }
.repo-table a:hover { color: var(--vp-c-brand-1); }
.security.sec-CLEAR { color: #2a8a3d; font-weight: 600; }
.security.sec-REVIEW { color: #c47c00; font-weight: 600; }
.security.sec-BLOCKED { color: #c63030; font-weight: 600; }
.rule-bars { display: flex; align-items: flex-end; gap: 4px; padding: 16px 24px 130px 70px; height: 400px; box-sizing: border-box; position: relative; }
.rule-col { flex: 1 1 0; min-width: 0; height: 100%; position: relative; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; }
.rule-col .bar { width: 100%; max-width: 30px; background: #2b5fff; border-radius: 1px 1px 0 0; min-height: 2px; }
.rule-label { position: absolute; top: calc(100% + 6px); right: 50%; transform-origin: 100% 0; transform: rotate(-50deg); font-size: 10px; white-space: nowrap; pointer-events: auto; color: var(--vp-c-text-2); }
.rule-label a { color: inherit; text-decoration: none; }
.rule-label a:hover { color: var(--vp-c-brand-1); }
.rule-detail { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 16px; }
.rule-detail th, .rule-detail td { padding: 4px 8px; border-bottom: 1px solid var(--vp-c-divider); }
.rule-detail th { background: var(--vp-c-bg); text-align: left; }
.rule-detail td.r, .rule-detail th.r { text-align: right; }
.g6-frame { width: 100%; height: 320px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); position: relative; }
.drift-frame { height: 600px; }
.legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; font-size: 12px; }
.legend-item { display: inline-flex; align-items: center; gap: 4px; }
.legend-item .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
</style>
