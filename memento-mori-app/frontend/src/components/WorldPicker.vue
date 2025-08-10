import { ref, computed } from 'vue'
<template>
  <div class="picker">
    <label>サーバー</label>
    <select v-model="server">
      <option v-for="s in servers" :key="s.value" :value="s.value">{{ s.label }}</option>
    </select>

    <label>ワールド</label>
    <select v-model.number="world" :disabled="allWorlds">
      <option value="0">全ワールド</option>
      <option v-for="n in 300" :key="n" :value="n">W{{ n }}</option>
    </select>

    <button @click="emitWorld">読み込み</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{ (e: 'select', worldId: number): void }>()

const servers = [
  { value: 1, label: 'Japan' },
  { value: 2, label: 'Korea' },
  { value: 3, label: 'Asia' },
  { value: 4, label: 'North America' },
  { value: 5, label: 'Europe' },
  { value: 6, label: 'Global' },
]

const server = ref(1)
const world = ref(0)
const allWorlds = computed(() => world.value === 0)

function toWorldId(s: number, w: number) {
  if (w === 0) return 0
  return s * 1000 + w
}

function emitWorld() {
  emit('select', toWorldId(server.value, world.value))
}
</script>

<style scoped>
.picker { display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
select, button { padding: .4rem .6rem; }
</style>