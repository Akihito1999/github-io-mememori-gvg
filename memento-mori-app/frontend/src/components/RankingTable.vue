<template>
  <div>
    <div v-if="loading">読み込み中...</div>
    <div v-else>
      <table>
        <thead>
          <tr>
            <th>Player</th>
            <th>BP</th>
            <th>Rank</th>
            <th>Quest</th>
            <th>Tower</th>
            <th>World</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in rows" :key="p.id">
            <td>{{ p.name }}</td>
            <td>{{ p.bp ?? '-' }}</td>
            <td>{{ p.rank ?? '-' }}</td>
            <td>{{ p.quest_id ?? '-' }}</td>
            <td>{{ p.tower_id ?? '-' }}</td>
            <td>{{ worldSuffix(p.id) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { getPlayerRanking } from '../api'

const props = defineProps<{ worldId: number }>()
const loading = ref(false)
const rows = ref<any[]>([])

async function load() {
  if (!props.worldId) return
  loading.value = true
  try {
    const data = await getPlayerRanking(props.worldId)
    const rankings = data?.data?.rankings
    const info = data?.data?.player_info || {}
    const bp = (rankings?.bp || []) as any[]
    rows.value = bp.map((x) => ({ ...info[x.id], ...x }))
  } finally {
    loading.value = false
  }
}

watch(() => props.worldId, load, { immediate: true })

function worldSuffix(id: number) { return String(id).slice(-3) }
</script>

<style scoped>
table { width: 100%; border-collapse: collapse; }
th, td { border-bottom: 1px solid #ddd; padding: .5rem; text-align: left; }
</style>