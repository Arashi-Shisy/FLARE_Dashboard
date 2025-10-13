<template>
  <div class="container">
    <div class="card">
      <h2 class="u-mt-0">お知らせ</h2>

      <div class="u-flex u-gap-2">
        <input v-model="text" placeholder="お知らせ内容" class="u-flex-1" />
        <button @click="post">投稿</button>
      </div>

      <div v-for="n in items" :key="n.id">
        <div class="u-flex u-gap-3 u-items-start">
          <img :src="n.user_avatar_url || placeholder" alt="" class="avatar avatar--md" />
          <div class="u-flex-1">
            <div class="u-fw-600">{{ n.text }}</div>
            <div class="u-hint">投稿者: {{ n.user_name || ('ID:' + n.user_id) }}</div>
            <div class="time">{{ new Date(n.created_at).toLocaleString() }}</div>

            <!-- ★ 作成者本人のみ「削除」ボタンを表示 -->
            <div v-if="me && me.id === n.user_id" class="u-mt-2">
              <button @click="remove(n)" class="btn btn-neutral">削除</button>
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
const me = ref(null)

async function loadMe(){
  const { data } = await api.get('/api/me')
  me.value = data.user
}
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
  try{
    await api.delete(`/api/announcements/${n.id}`)
    await load()
  }catch(e){
    // キャンセル等は無視
  }
}
socket.on('new_announcement', (n) => {
  items.value.unshift(n)
})

onMounted(async () => {
  await Promise.all([loadMe(), load()])
})
</script>
