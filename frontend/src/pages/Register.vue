<template>
  <div class="container">
    <div class="card" style="max-width:420px;margin:2rem auto">
      <h2 style="margin:0 0 1rem 0">ユーザー登録</h2>
      <div class="row">
        <input v-model="username" placeholder="ユーザー名" />
        <input v-model="password" placeholder="パスワード" type="password" />
        <button @click="register">登録してログイン</button>
        <div class="hint">既にアカウントあり？ <RouterLink to="/login">ログイン</RouterLink></div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { api } from '../utils/api'
import { useRouter } from 'vue-router'
const router = useRouter()
const username = ref('')
const password = ref('')
async function register(){
  try{
    await api.post('/api/register',{ username: username.value, password: password.value })
    router.push('/')
  }catch(e){
    alert('登録に失敗しました')
  }
}
</script>
