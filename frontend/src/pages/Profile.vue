<template>
  <div class="container">
    <div class="card">
      <h2 style="margin-top:0">マイページ</h2>

      <div style="display:flex; gap:1rem; align-items:center">
        <img :src="me?.avatar_url || fallback" alt="avatar" style="width:72px;height:72px;border-radius:50%;object-fit:cover;background:#222" />
        <div>
          <div style="font-weight:700">{{ me?.username }}</div>
          <div class="hint">生年月日: <input type="date" v-model="form.birthday" /></div>
          <div class="hint"><label><input type="checkbox" v-model="form.notifications_enabled" /> ブラウザ通知</label></div>
        </div>
      </div>

      <div style="margin-top:1rem">
        <label class="hint">プロフィール画像を選択</label>
        <input type="file" accept="image/*" @change="onFile" />
      </div>

      <div style="margin-top:1rem; display:flex; gap:.5rem">
        <button @click="save" class="btn btn-primary">保存</button>
        <button @click="logout" class="btn btn-neutral">ログアウト</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../utils/api'
import { toast } from '../utils/toast'

const me = ref(null)
const form = ref({ birthday: '', notifications_enabled: false })
const avatarFile = ref(null)
const fallback = '/img/avatar_placeholder.png'

async function load(){
  const { data } = await api.get('/api/me')
  me.value = data.user
  if (me.value){
    form.value.birthday = me.value.birthday || ''
    form.value.notifications_enabled = !!me.value.notifications_enabled
  }
}
function onFile(e){
  avatarFile.value = e.target.files?.[0] || null
}
async function save(){
  const fd = new FormData()
  fd.append('birthday', form.value.birthday || '')
  fd.append('notifications_enabled', form.value.notifications_enabled ? '1' : '0')
  if (avatarFile.value){
    fd.append('avatar', avatarFile.value)
  }
  try {
    const { data } = await api.post('/api/me', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (data?.avatar_url) me.value.avatar_url = data.avatar_url
    await load()
    toast('保存しました', 'success')
  } catch (e) {
    const status = e?.response?.status
    if (status === 413) {
      toast('ファイルサイズが大きすぎます', 'error')
    } else {
      toast('保存に失敗しました', 'error')
    }
  }
}
async function logout(){
  try { await api.post('/api/logout') } catch {}
  window.location.assign('/')
}
onMounted(load)
</script>
