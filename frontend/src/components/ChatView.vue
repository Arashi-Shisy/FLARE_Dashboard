<template>
  <div class="container">
    <div class="card" style="height:70vh;display:flex;flex-direction:column">
      <h3 style="margin-top:0">コミュニティチャット</h3>

      <div style="flex:1;overflow:auto;display:flex;flex-direction:column-reverse">
        <div
          v-for="m in messages"
          :key="m.id"
          :class="['chat-bubble', m.user_id===me?.id? 'chat-right':'chat-left']"
        >
          <!-- 他人のメッセージ: アバター + 本文 を横並びで表示 -->
          <template v-if="m.user_id !== me?.id">
            <div style="display:flex; gap:.5rem; align-items:flex-start">
              <img
                :src="m.user_avatar_url || placeholder"
                alt=""
                style="width:28px;height:28px;border-radius:50%;object-fit:cover;background:#222;flex:none"
              />
              <div style="flex:1;min-width:0">
                <div class="hint">{{ m.user_name || ('ID:' + m.user_id) }}</div>
                <div style="word-wrap:break-word;white-space:pre-wrap">{{ m.content }}</div>
                <div class="time">{{ new Date(m.created_at).toLocaleString() }}</div>
              </div>
            </div>
          </template>

          <!-- 自分のメッセージ: 既存の見た目を維持（アバターは出さない） -->
          <template v-else>
            <div style="word-wrap:break-word;white-space:pre-wrap">{{ m.content }}</div>
            <div class="time">{{ new Date(m.created_at).toLocaleString() }}</div>
            <div class="hint"><a href="#" @click.prevent="remove(m)">削除</a></div>
          </template>
        </div>
      </div>

      <div style="display:flex;gap:.5rem">
        <input v-model="text" placeholder="メッセージを入力..." @keyup.enter="send"/>
        <button @click="send">送信</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api, socket, notify } from '../utils/api'

const text = ref('')
const messages = ref([])
const me = ref(null)
const placeholder = '/img/avatar_placeholder.png' // 任意のプレースホルダー

async function load(){
  const meRes = await api.get('/api/me'); me.value = meRes.data.user
  const { data } = await api.get('/api/chat?limit=100')
  messages.value = data.items || []
}
async function send(){
  if(!text.value) return
  await api.post('/api/chat', { content: text.value })
  text.value=''
  await load()
}
async function remove(m){
  await api.delete(`/api/chat/${m.id}`)
  await load()
}

onMounted(async () => {
  await load()
  socket.on('chat_message', (payload)=>{
    // 先頭に差し込む（既存の column-reverse と整合）
    messages.value = [payload, ...messages.value]
    if (payload.user_id !== me.value?.id) {
      notify('新着メッセージ', payload.content)
    }
  })
})
</script>
