<template>
  <div class="container">
    <div class="card" v-if="event">
      <h2 class="u-mt-0">{{ event.name }}</h2>
      <div class="u-hint">主催: {{ event.created_by_name || ('ID:' + event.created_by) }}</div>
      <div class="u-hint">開始: {{ new Date(event.start_at).toLocaleString() }} / 終了: {{ new Date(event.end_at).toLocaleString() }}</div>
      <p class="u-prewrap">{{ event.description }}</p>
      <div v-if="event.location">場所: {{ event.location }}</div>
      <div v-if="event.url"><a :href="event.url" target="_blank" rel="noreferrer">関連リンク</a></div>

      <div class="u-mt-3">
        <button @click="toggle">{{ event.going ? '参加取消' : '参加表明' }}</button>
        <span class="badge u-ml-2">参加者 {{ attendeeCount }} 名</span>
      </div>
    </div>

    <div>
      <h3 class="u-mb-2">参加者リスト（{{ attendeeCount }}）</h3>
      <div v-if="attendees.length === 0" class="u-hint">まだ参加者はいません</div>
      <ul v-else class="u-list-reset">
        <li v-for="a in attendees" :key="a.user_id" class="u-py-2 u-border-b u-flex u-gap-3 u-items-center">
          <img :src="a.avatar_url || placeholder" alt="" class="avatar avatar--sm" />
          <div class="u-flex-1">
            <div class="u-fw-600">{{ a.user_name || ('ID:' + a.user_id) }}</div>
            <div class="time">参加: {{ new Date(a.joined_at).toLocaleString() }}</div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../utils/api'
import { useRoute } from 'vue-router'
import { toast } from '../utils/toast'

const route = useRoute()
const event = ref(null)
const attendees = ref([])
const attendeeCount = ref(0)
const placeholder = '/img/avatar_placeholder.png'

async function loadEvent(){
  const { data } = await api.get(`/api/events/${route.params.id}`)
  event.value = data.event
  if (typeof data.event?.attendee_count === 'number') {
    attendeeCount.value = data.event.attendee_count
  }
}
async function loadAttendees(){
  const { data } = await api.get(`/api/events/${route.params.id}/attendees`)
  attendees.value = data.items || []
  attendeeCount.value = data.count || attendees.value.length
}
async function load(){
  await Promise.all([loadEvent(), loadAttendees()])
}
async function toggle(){
  const { data } = await api.post(`/api/events/${route.params.id}/attend`)
  await load()
  if (data?.going) {
    toast('参加表明しました', 'success')
  } else {
    toast('参加を取り消しました', 'info')
  }
}
onMounted(load)
</script>
