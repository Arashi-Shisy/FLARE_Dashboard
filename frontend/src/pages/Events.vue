<template>
  <div class="container">
    <div class="card">
      <h3 style="margin:0 0 1rem 0">イベント一覧</h3>
      <div class="row">
        <div class="col" style="min-width:280px">
          <input v-model="form.name" placeholder="イベント名" />
        </div>
        <div class="col" style="min-width:220px">
          <input v-model="form.start_at" type="datetime-local" />
        </div>
        <div class="col" style="min-width:220px">
          <input v-model="form.end_at" type="datetime-local" />
        </div>
      </div>
      <div class="row">
        <div class="col"><input v-model="form.location" placeholder="場所（オンラインURL可）" /></div>
        <div class="col"><input v-model="form.url" placeholder="URL（任意）" /></div>
      </div>
      <textarea v-model="form.description" rows="3" placeholder="説明"></textarea>
      <div style="margin-top:.5rem"><button @click="create">イベント登録</button></div>
    </div>

    <div class="card" style="margin-top:1rem">
      <div v-for="e in items" :key="e.id" class="card" style="margin:.5rem 0;background:#161616">
        <EventCard :event="e" @toggle="toggleAttend(e)" />
        <div style="display:flex;gap:.5rem;margin-top:.5rem">
          <RouterLink class="badge" :to="`/events/${e.id}`">詳細</RouterLink>
          <button @click="remove(e)" style="background:#2a2a2a;border:1px solid #444;color:#ddd">削除（作成者のみ）</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api, notify } from '../utils/api'
import EventCard from '../components/EventCard.vue'

const items = ref([])
const form = ref({ name:'', start_at:'', end_at:'', description:'', location:'', url:'' })

async function load(){
  const { data } = await api.get('/api/events?upcoming=true')
  items.value = data.items || []
}
async function create(){
  if(!form.value.name || !form.value.start_at || !form.value.end_at) return alert('必須項目を入力してください')
  const toIso = (v)=> new Date(v).toISOString()
  await api.post('/api/events', { ...form.value, start_at: toIso(form.value.start_at), end_at: toIso(form.value.end_at) })
  await load()
  form.value = { name:'', start_at:'', end_at:'', description:'', location:'', url:'' }
  notify('新しいイベント', 'イベントが登録されました')
}
async function toggleAttend(e){
  await api.post(`/api/events/${e.id}/attend`)
  await load()
}
async function remove(e){
  try{
    await api.delete(`/api/events/${e.id}`)
    await load()
  }catch(err){
    alert('削除できません（作成者のみ）')
  }
}
onMounted(load)
</script>
