import { createRouter, createWebHistory } from 'vue-router'
import Login from './pages/Login.vue'
import Register from './pages/Register.vue'
import Dashboard from './pages/Dashboard.vue'
import Events from './pages/Events.vue'
import EventDetail from './pages/EventDetail.vue'
import Announcements from './pages/Announcements.vue'
import Profile from './pages/Profile.vue'
import Chat from './components/ChatView.vue'
import { api } from './utils/api'

const routes = [
  { path: '/', name:'home', component: Dashboard, meta:{ auth:true } },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/events', component: Events, meta:{ auth:true } },
  { path: '/events/:id', component: EventDetail, meta:{ auth:true } },
  { path: '/announcements', component: Announcements, meta:{ auth:true } },
  { path: '/profile', component: Profile, meta:{ auth:true } },
  { path: '/chat', component: Chat, meta:{ auth:true } }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to, from, next) => {
  if (!to.meta.auth) return next()
  try {
    const { data } = await api.get('/api/me')
    if (data.user) return next()
    return next('/login')
  } catch (e) {
    return next('/login')
  }
})

export default router
