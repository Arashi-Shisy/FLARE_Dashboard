<template>
<div>
  <div style="display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-weight:700">{{ event.name }}</div>
      <div class="hint">主催: {{ event.created_by_name || ('ID:' + event.created_by) }}</div>
      <div class="hint">開始: {{ new Date(event.start_at).toLocaleString() }}</div>
    </div>
    <button @click="$emit('toggle')">{{ event.going ? '参加取消' : '参加表明' }}</button>
  </div>
</div>
</template>
<script setup>
defineProps({ event: { type:Object, required:true } })
</script>
