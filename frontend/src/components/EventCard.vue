<template>
  <div class="card event-card">
    <div class="event-row">
      <!-- 左：イベント情報 -->
      <div class="event-info">
        <div class="event-title" :title="event.name">{{ event.name }}</div>
        <div class="hint">
          {{ new Date(event.start_at).toLocaleString() }} 〜 {{ new Date(event.end_at).toLocaleString() }}
        </div>
        <div class="hint">主催: {{ event.created_by_name || ('ID:' + event.created_by) }}</div>

        <div v-if="event.location" class="hint" style="margin-top:.25rem">場所: {{ event.location }}</div>
        <div v-if="event.url" class="hint" style="margin-top:.25rem">
          <a :href="event.url" target="_blank" rel="noreferrer">関連リンク</a>
        </div>
      </div>

      <!-- 右端：ボタン縦並び（参加→削除）。削除は作成者本人のみ -->
      <div class="event-controls">
        <button class="btn btn-primary" @click="$emit('toggle')">
          {{ event.going ? '参加取消' : '参加する' }}
        </button>
        <button
          v-if="me && me.id === event.created_by"
          class="btn btn-neutral"
          @click="removeEvent"
        >
          削除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../utils/api'

const props = defineProps({
  event: { type: Object, required: true },
})
const me = ref(null)

async function loadMe(){
  const { data } = await api.get('/api/me')
  me.value = data.user
}

async function removeEvent(){
  try{
    await api.delete(`/api/events/${props.event.id}`)
    // 親で再取得する前提。必要なら emit('removed', props.event.id) で通知
  }catch(e){
    /* confirm キャンセル等は無視 */
  }
}

onMounted(loadMe)
</script>
