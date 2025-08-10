<!-- memento-mori-app/frontend/src/App.vue -->
<template>
  <main class="container">
    <h1>Memento Mori — Guild Battle (Local GvG)</h1>
    <WorldPicker @select="onSelect" />

    <section v-if="worldId" class="cards">
      <article class="card">
        <h2>Guild Battle — Castles</h2>
        <LocalGvgBoard :worldId="worldId!" />
      </article>

      <article class="card">
        <h2>Player BP Ranking (sample)</h2>
        <RankingTable :worldId="worldId!" />
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import WorldPicker from './components/WorldPicker.vue'
import RankingTable from './components/RankingTable.vue'
import LocalGvgBoard from './components/LocalGvgBoard.vue'

const worldId = ref<number | null>(null)
function onSelect(id: number) { worldId.value = id }
</script>

<style>
:root { color-scheme: light dark; }
body { margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif; }
.container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
h1 { font-size: 1.6rem; margin-bottom: 1rem; }
.cards { display: grid; gap: 1rem; grid-template-columns: 1fr; }
.card { padding: 1rem; border: 1px solid #e5e5e5; border-radius: 12px; }
@media (min-width: 1000px) { .cards { grid-template-columns: 1fr 1fr; } }
</style>
