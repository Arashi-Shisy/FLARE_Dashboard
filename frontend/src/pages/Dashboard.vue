<template>
  <div class="container">
    <div class="grid2">
      <div class="card">
        <h2 style="margin-top:0">今週のイベント</h2>
        <EventCard v-for="e in events" :key="e.id" :event="e" @toggle="toggle(e)" />
      </div>
      <div class="card">
        <h2 style="margin-top:0">最新お知らせ</h2>
        <ul style="list-style:none;margin:0;padding:0">
          <li v-for="n in announcements" :key="n.id" style="margin:.5rem 0">
            <div style="display:flex; gap:.5rem; align-items:flex-start">
              <img :src="n.user_avatar_url || placeholder" alt="" style="width:24px;height:24px;border-radius:50%;object-fit:cover;background:#222" />
              <div>
                <div style="font-weight:600">{{ n.text }}</div>
                <div class="hint">投稿者: {{ n.user_name || ('ID:' + n.user_id) }}</div>
                <div class="time">{{ new Date(n.created_at).toLocaleString() }}</div>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../utils/api'
import EventCard from '../components/EventCard.vue'
import { toast } from '../utils/toast'

const events = ref([])
const announcements = ref([])
const placeholder = '/img/avatar_placeholder.png'

async function load(){
  const { data } = await api.get('/api/home')
  announcements.value = data.announcements || []
  events.value = data.events || []
}
async function toggle(e){
  const { data } = await api.post(`/api/events/${e.id}/attend`)
  const res = await api.get(`/api/events/${e.id}`)
  const idx = events.value.findIndex(x => x.id === e.id)
  if (idx >= 0) events.value[idx] = res.data.event
  if (data?.going) {
    toast('参加表明しました', 'success')
  } else {
    toast('参加を取り消しました', 'info')
  }
}
onMounted(load)
</script>
