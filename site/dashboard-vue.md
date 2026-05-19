---
title: Auditor dashboard
sidebar: false
aside: false
---

<script setup>
// Data is generated at build time from auditor/reports/dashboard.json
// and dropped at site/.vitepress/theme/data/dashboard.json (gitignored).
// See site/build.sh for the wire-up.
import data from './.vitepress/theme/data/dashboard.json'
</script>

<DashboardPanels :data="data" />
