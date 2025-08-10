<!-- memento-mori-app/frontend/src/components/LocalGvgBoard.vue -->
<template>
  <div class="gvg">
    <div class="toolbar">
      <div class="hint">
        World: {{ worldId }}
        <span v-if="updatedAt"> / Updated: {{ updatedAt?.toLocaleString() }}</span>
      </div>
      <div class="legend">
        <span class="pill idle">Idle</span>
        <span class="pill battle">Battle</span>
        <span class="pill fallen">Fallen</span>
        <span class="pill counter">Counter</span>
        <span class="pill counterok">Counter OK</span>
      </div>
      <div class="right">
        <button @click="toggleLive">{{ live ? '⏸ 停止' : '▶ 再開' }}</button>
      </div>
    </div>

    <div v-if="connecting" class="loading">接続中...</div>

    <div v-else class="grid">
      <div
        v-for="c in castles"
        :key="c.CastleId"
        class="cell"
        :class="stateClass(c.GvgCastleState)"
      >
        <header>
          <strong>{{ castleName(c.CastleId) }}</strong>
          <small>#{{ c.CastleId }}</small>
        </header>
        <div class="row">
          <div class="label">Holder</div>
          <div class="value">{{ guildName(c.GuildId) || '—' }}</div>
        </div>
        <div class="row">
          <div class="label">Attacker</div>
          <div class="value">{{ guildName(c.AttackerGuildId) || '—' }}</div>
        </div>
        <div class="row counts">
          <div>DEF: {{ c.DefensePartyCount }}</div>
          <div>ATK: {{ c.AttackPartyCount }}</div>
          <div>KO: {{ c.KoCount ?? 0 }}</div>
        </div>
        <footer>{{ stateLabel(c.GvgCastleState) }}</footer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { wsUrl } from '../api'

const props = defineProps<{ worldId: number }>()

const updatedAt = ref<Date | null>(null)
const castles = ref<any[]>([])
const guilds = ref<Record<string, string>>({})
const live = ref(true)
const connecting = ref(false)
let sock: WebSocket | null = null

function makeStreamId(castleId: number, block: number, group: number, gclass: number, world: number) {
  // 0..4 castle(5), 5..7 block(3), 8..15 group(8), 16..18 class(3), 19..31 world(13)
  const id =
    (castleId & 0x1f) |
    ((block & 0x7) << 5) |
    ((group & 0xff) << 8) |
    ((gclass & 0x7) << 16) |
    ((world & 0x1fff) << 19)
  const buf = new ArrayBuffer(4)
  const view = new DataView(buf)
  view.setUint32(0, id, true) // little-endian
  return buf
}

function parseMessage(buf: ArrayBuffer) {
  const view = new DataView(buf)
  let off = 0
  const dec = new TextDecoder()

  while (off + 4 <= view.byteLength) {
    const sid = view.getUint32(off, true); off += 4
    const castle = sid & 0x1f
    const block = (sid >> 5) & 0x7
    const group = (sid >> 8) & 0xff
    const gclass = (sid >> 16) & 0x7
    const world = (sid >> 19) & 0x1fff

    if (castle === 0) {
      // Guild Information Message
      if (off + 5 > view.byteLength) break
      const gid = view.getUint32(off, true); off += 4
      const nameLen = view.getUint8(off); off += 1
      if (off + nameLen > view.byteLength) break
      const name = dec.decode(new Uint8Array(buf, off, nameLen)); off += nameLen
      if (gid === 0) {
        guilds.value = {}
      } else {
        guilds.value = { ...guilds.value, [String(gid)]: name }
      }
    } else {
      // Castle Status Message
      if (off + 20 > view.byteLength) break
      const holder = view.getUint32(off, true); off += 4
      const attacker = view.getUint32(off, true); off += 4
      const fallen = view.getUint32(off, true); off += 4
      const def = view.getUint16(off, true); off += 2
      const atk = view.getUint16(off, true); off += 2
      const state = view.getUint8(off); off += 1
      off += 1 // reserved
      const ko = view.getUint16(off, true); off += 2

      const next = {
        CastleId: castle,
        GuildId: holder,
        AttackerGuildId: attacker,
        UtcFallenTimeStamp: fallen,
        DefensePartyCount: def,
        AttackPartyCount: atk,
        GvgCastleState: state,
        KoCount: ko,
        block, group, gclass, world
      }
      const idx = castles.value.findIndex(x => x.CastleId === castle)
      if (idx >= 0) castles.value[idx] = next; else castles.value.push(next)
    }
  }
  updatedAt.value = new Date()
}

function guildName(id: number) { return id ? guilds.value[String(id)] : '' }
function castleName(id: number) { return castleNames[id] ?? `Castle ${id}` }
function stateLabel(s: number) { return ['Idle','Battle','Fallen','Counter','Counter OK'][s] ?? 'Unknown' }
function stateClass(s: number) { return ['idle','battle','fallen','counter','counterok'][s] ?? 'idle' }

const castleNames: Record<number, string> = {
  1: 'Brussell', 2: 'Wissekerke', 3: 'Modave', 4: 'Chimay', 5: 'Gravensteen',
  6: 'Cambre', 7: 'Quentin', 8: 'Lambert', 9: 'Saint-Jacques', 10: 'Michael',
  11: 'Namur', 12: 'Charleroi', 13: 'Alzette', 14: 'Hainaut', 15: 'Wavre',
  16: 'Mons', 17: 'Christophe', 18: 'Kortrijk', 19: 'Ypres', 20: 'Salvador', 21: 'Bavo'
}

function openWs() {
  closeWs()
  connecting.value = true
  const url = wsUrl('/ws/gvg')
  sock = new WebSocket(url)
  sock.binaryType = 'arraybuffer'
  sock.onopen = () => {
    connecting.value = false
    // 全城購読（block=0, group=0, class=0）
    const sub = makeStreamId(0, 0, 0, 0, props.worldId)
    sock!.send(sub)
  }
  sock.onmessage = (ev) => {
    if (typeof ev.data !== 'string') parseMessage(ev.data)
  }
  sock.onclose = () => { if (live.value) reconnectLater() }
  sock.onerror = () => { /* ignore */ }
}

let retryTimer: any = null
function reconnectLater() {
  clearTimeout(retryTimer)
  retryTimer = setTimeout(() => { if (live.value) openWs() }, 1500)
}

function closeWs() {
  if (sock) { try { sock.close() } catch {} finally { sock = null } }
}

function toggleLive() {
  live.value = !live.value
  if (live.value) openWs(); else closeWs()
}

onMounted(() => { if (live.value) openWs() })
onUnmounted(() => closeWs())
watch(() => props.worldId, () => { if (live.value) openWs() })
</script>

<style scoped>
.toolbar { display:flex; justify-content: space-between; align-items: center; margin-bottom: .5rem; gap: .5rem; flex-wrap: wrap; }
.legend { display: flex; gap: .4rem; }
.pill { padding: .2rem .5rem; border-radius: 999px; font-size: .8rem; border: 1px solid #ddd; }
.pill.idle{ background:#f6f6f6; }
.pill.battle{ background:#ffe9cc; }
.pill.fallen{ background:#ffe0e0; }
.pill.counter{ background:#e7f0ff; }
.pill.counterok{ background:#e1ffe7; }
.loading { padding: .8rem; }
.grid { display:grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; }
.cell { border:1px solid #e5e5e5; border-radius: 10px; padding:.6rem; display:flex; flex-direction: column; gap:.35rem; }
.cell header { display:flex; justify-content: space-between; align-items:center; font-size:.95rem; }
.row { display:flex; justify-content: space-between; align-items:center; gap:.5rem; }
.row .label { color:#666; }
.row.counts { display:flex; gap: .8rem; font-size: .9rem; }
.cell footer { margin-top:.2rem; font-size:.85rem; color:#555; }
.cell.idle{ }
.cell.battle{ outline: 2px solid #ffcc80; }
.cell.fallen{ outline: 2px solid #ff9e9e; }
.cell.counter{ outline: 2px solid #a3c4ff; }
.cell.counterok{ outline: 2px solid #9bffb4; }
@media (min-width: 1100px){ .grid{ grid-template-columns: repeat(4, 1fr);} }
</style>
