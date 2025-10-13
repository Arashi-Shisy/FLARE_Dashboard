<template>
  <div class="card">
    <h3 class="u-mt-0">ブラウザ通知 テスト</h3>
    <div class="u-hint">ボタンを押すと通知を表示します（ブラウザの許可が必要）</div>
    <button @click="test">通知テスト</button>
  </div>
</template>
<script setup>
import { notify } from '../utils/api'
function test(){
  notify('FLARE 通知テスト', 'これはテスト通知です')
}
</script>
