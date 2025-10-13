<template>
  <div>
    <nav class="nav">
      <div class="nav-inner">
        <div class="brand">FLARE Dashboard</div>
        <div class="u-flex u-gap-2">
          <RouterLink class="link" to="/">Home</RouterLink>
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
