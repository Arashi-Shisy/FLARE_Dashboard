<template>
  <div class="container">
    <div>
      <h2 class="u-mb-4">ログイン</h2>
      <div class="row">
        <input v-model="username" placeholder="ユーザー名" />
        <input v-model="password" placeholder="パスワード" type="password" />
        <button @click="login">ログイン</button>
        <div class="u-hint">初めての方は <RouterLink to="/register">ユーザー登録</RouterLink></div>
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
async function login(){
  try{
    await api.post('/api/login',{ username: username.value, password: password.value })
    router.push('/')
  }catch(e){
    alert('ログインに失敗しました')
  }
}
</script>
