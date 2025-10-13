<template>
  <div class="card event-card">
    <div class="event-row">
      <!-- 左：イベント情報 -->
      <div class="event-info">
        <div class="event-title" :title="event.name">{{ event.name }}</div>
        <div class="hint">
          {{ new Date(event.start_at).toLocaleString() }} 〜 {{ new Date(event.end_at).toLocaleString() }}
        </div>
        <div class="hint">
          主催: {{ event.created_by_name || ('ID:' + event.created_by) }}
        </div>

        <div v-if="event.location" class="hint" style="margin-top:.25rem">
          場所: {{ event.location }}
        </div>
        <div v-if="event.url" class="hint" style="margin-top:.25rem">
          <a :href="event.url" target="_blank" rel="noreferrer">関連リンク</a>
        </div>
      </div>

      <!-- 右端：ボタン縦並び（参加トグル→削除）。削除は作成者本人のみ -->
      <div class="event-controls">
        <button class="btn btn-primary" @click="$emit('toggle')">
          {{ event.going ? '参加取消' : '参加表明' }}
        </button>

        <button
          v-if="me && me.id === event.created_by"
          class="btn btn-neutral"
          @click="onDelete"
        >
          削除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../utils/api.js'
import { toast } from '../utils/toast.js'
import { reloadPage } from '../utils/navigation.js'

const props = defineProps({
  event: { type: Object, required: true },
})

const me = ref(null)

onMounted(async () => {
  try {
    const { data } = await api.get('/api/me')
    me.value = data?.user ?? null
  } catch {
    me.value = null
  }
})

async function onDelete() {
  try {
    // 確認モーダルは api.js 内で実施される想定
    await api.delete(`/api/events/${props.event.id}`)
    toast('削除しました', 'success')
    reloadPage()
  } catch (e) {
    // ユーザーが確認モーダルでキャンセルした場合は何もしない
    if (e && e.cancelled) return
    console.error(e)
    toast('削除に失敗しました', 'error')
  }
}
</script>


