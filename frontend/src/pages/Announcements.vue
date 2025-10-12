<template>
  <div class="container">
    <div class="card">
      <h2 style="margin-top:0">お知らせ</h2>
      <div style="display:flex; gap:.5rem">
        <input v-model="text" placeholder="お知らせ内容" style="flex:1" />
        <button @click="post">投稿</button>
      </div>
      <div v-for="n in items" :key="n.id" class="card" style="margin:.5rem 0;background:#161616">
        <div style="display:flex; gap:.75rem; align-items:flex-start">
          <img :src="n.user_avatar_url || placeholder" alt="" style="width:32px;height:32px;border-radius:50%;object-fit:cover;background:#222" />
          <div style="flex:1">
            <div style="font-weight:600">{{ n.text }}</div>
            <div class="hint">投稿者: {{ n.user_name || ('ID:' + n.user_id) }}</div>
            <div class="time">{{ new Date(n.created_at).toLocaleString() }}</div>
            <div style="margin-top:.5rem">
              <button @click="remove(n)" style="background:#2a2a2a;border:1px solid #444;color:#ddd">削除（作成者のみ）</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api, socket } from '../utils/api'
const items = ref([])
const text = ref('')
const placeholder = '/img/avatar_placeholder.png'
async function load(){
  const { data } = await api.get('/api/announcements')
  items.value = data.items || []
}
async function post(){
  if(!text.value.trim()) return
  await api.post('/api/announcements', { text: text.value.trim() })
  text.value = ''
  await load()
}
async function remove(n){
  await api.delete(`/api/announcements/${n.id}`)
  await load()
}
socket.on('new_announcement', (n) => {
  items.value.unshift(n)
})
onMounted(load)
</script>
