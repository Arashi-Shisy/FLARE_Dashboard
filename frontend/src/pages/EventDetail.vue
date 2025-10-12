<template>
  <div class="container">
    <div class="card" v-if="event">
      <h2 style="margin-top:0">{{ event.name }}</h2>
      <div class="hint">主催: {{ event.created_by_name || ('ID:' + event.created_by) }}</div>
      <div class="hint">開始: {{ new Date(event.start_at).toLocaleString() }} / 終了: {{ new Date(event.end_at).toLocaleString() }}</div>
      <p style="white-space:pre-wrap">{{ event.description }}</p>
      <div v-if="event.location">場所: {{ event.location }}</div>
      <div v-if="event.url"><a :href="event.url" target="_blank" rel="noreferrer">関連リンク</a></div>
      <div style="margin-top:.75rem">
        <button @click="toggle">{{ event.going ? '参加取消' : '参加する' }}</button>
        <span class="badge" style="margin-left:.5rem">参加者 {{ attendeeCount }} 名</span>
      </div>
    </div>
    <div class="card" style="margin-top:1rem">
      <h3 style="margin:0 0 .5rem 0">参加者リスト（{{ attendeeCount }}）</h3>
      <div v-if="attendees.length === 0" class="hint">まだ参加者はいません</div>
      <ul v-else style="list-style:none;padding:0;margin:0">
        <li v-for="a in attendees" :key="a.user_id" style="padding:.5rem 0;border-bottom:1px solid #333;display:flex;gap:.75rem;align-items:center">
          <img :src="a.avatar_url || placeholder" alt="" style="width:28px;height:28px;border-radius:50%;object-fit:cover;background:#222" />
          <div style="flex:1">
            <div style="font-weight:600">{{ a.user_name || ('ID:' + a.user_id) }}</div>
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
  await api.post(`/api/events/${route.params.id}/attend`)
  await load()
}
onMounted(load)
</script>
