<template>
  <div class="container">
    <h2 class="u-mt-0">イベント一覧</h2>

    <!-- ▼ 新規イベント作成フォーム -->
    <div>
      <h3 class="u-mt-0 u-mb-3">新規イベント</h3>
      <div class="row">
        <div class="col">
          <label class="u-hint">イベント名</label>
          <input v-model="form.name" placeholder="例: FLARE ミートアップ" />
        </div>
        <div class="col">
          <label class="u-hint">開始日時</label>
          <input v-model="form.start_at" type="datetime-local" />
        </div>
        <div class="col">
          <label class="u-hint">終了日時</label>
          <input v-model="form.end_at" type="datetime-local" />
        </div>
      </div>

      <div>
        <div class="col">
          <label class="u-hint">場所（任意）</label>
          <input v-model="form.location" placeholder="例: オンライン / 会議室A" />
        </div>
        <div class="col">
          <label class="u-hint">関連URL（任意）</label>
          <input v-model="form.url" placeholder="https://..." />
        </div>
      </div>

      <div class="u-mt-2">
        <label class="u-hint">説明（任意）</label>
        <textarea v-model="form.description" rows="3" placeholder="イベントの説明を入力..."></textarea>
      </div>

      <div class="actions-right u-gap-2">
        <button class="btn btn-primary" @click="create">作成</button>
        <button class="btn btn-neutral" @click="resetForm">クリア</button>
      </div>
    </div>

    <!-- ▼ 一覧 -->
    <div v-if="events.length === 0" class="u-hint">イベントはまだありません</div>

    <div v-for="e in events" :key="e.id">
      <!-- 参加/削除は EventCard の右端ボタン列に統一（削除は作成者のみ表示） -->
      <EventCard :event="e" @toggle="toggle(e)" />

      <!-- 一覧側は「詳細」だけ（※削除は EventCard 側に一本化） -->
      <div class="actions-right">
        <router-link :to="`/events/${e.id}`" class="btn btn-neutral">詳細</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../utils/api'
import { toast } from '../utils/toast'
import EventCard from '../components/EventCard.vue'

const events = ref([])

const form = ref({
  name: '',
  start_at: '', // datetime-local (例: 2025-10-12T18:30)
  end_at: '',
  description: '',
  location: '',
  url: ''
})

function resetForm(){
  form.value = { name:'', start_at:'', end_at:'', description:'', location:'', url:'' }
}

async function load(){
  const { data } = await api.get('/api/events?include_past=false')
  events.value = data.items || []
}

function toIsoZ(dtLocal){
  // datetime-local を UTC の ISO(Z付) に
  try{
    return new Date(dtLocal).toISOString()
  }catch{ return '' }
}

async function create(){
  // バリデーション
  if(!form.value.name.trim()){
    toast('イベント名を入力してください', 'error'); return
  }
  if(!form.value.start_at || !form.value.end_at){
    toast('開始/終了日時を入力してください', 'error'); return
  }
  const startIso = toIsoZ(form.value.start_at)
  const endIso = toIsoZ(form.value.end_at)
  if(!startIso || !endIso){
    toast('日時の形式が正しくありません', 'error'); return
  }
  try{
    await api.post('/api/events', {
      name: form.value.name.trim(),
      start_at: startIso,
      end_at: endIso,
      description: form.value.description || '',
      location: form.value.location || '',
      url: form.value.url || ''
    })
    toast('イベントを作成しました', 'success')
    resetForm()
    await load()
  }catch(e){
    toast('作成に失敗しました', 'error')
  }
}

async function toggle(e){
  try{
    const { data } = await api.post(`/api/events/${e.id}/attend`)
    // 対象イベントのみ再取得して差し替え
    const res = await api.get(`/api/events/${e.id}`)
    const idx = events.value.findIndex(x => x.id === e.id)
    if (idx >= 0) events.value[idx] = res.data.event
    // トースト
    if (data?.going) {
      toast('参加表明しました', 'success')
    } else {
      toast('参加を取り消しました', 'info')
    }
  }catch{
    toast('操作に失敗しました', 'error')
  }
}

onMounted(load)
</script>


