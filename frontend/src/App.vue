<template>
  <div>
    <nav class="nav">
      <div class="nav-inner">
        <div class="brand">FLARE Dashboard</div>
        <div style="display:flex;gap:.5rem">
          <RouterLink class="link" :class="{active: $route.path==='/' }" to="/">Home</RouterLink>
          <RouterLink class="link" to="/events">Events</RouterLink>
          <RouterLink class="link" to="/announcements">News</RouterLink>
          <RouterLink class="link" to="/chat">Chat</RouterLink>
          <RouterLink class="link" to="/profile">MyPage</RouterLink>
        </div>
      </div>
    </nav>
    <RouterView/>
  </div>
</template>

<script setup>
</script>
