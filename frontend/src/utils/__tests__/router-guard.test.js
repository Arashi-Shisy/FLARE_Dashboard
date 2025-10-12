import { createRouter, createWebHistory } from 'vue-router'
import { describe, it, expect, vi } from 'vitest'

const Dummy = { template: '<div>dummy</div>' }

// ★ ここが修正ポイント：utils への相対パス
vi.mock('../../utils/api.js', () => {
  const get = vi.fn()
  return { api: { get } }
})
import { api } from '../../utils/api.js'

function makeRouter() {
  const routes = [
    { path: '/', component: Dummy, meta: { auth: true } },
    { path: '/login', component: Dummy }
  ]
  const router = createRouter({ history: createWebHistory(), routes })

  router.beforeEach(async (to, from, next) => {
    if (!to.meta.auth) return next()
    try {
      const { data } = await api.get('/api/me')
      if (data.user) return next()
      return next('/login')
    } catch {
      return next('/login')
    }
  })
  return router
}

describe('router guard', () => {
  it('未ログインなら /login', async () => {
    api.get.mockResolvedValue({ data: { user: null } })
    const router = makeRouter()
    await router.push('/')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('ログイン済みなら通す', async () => {
    api.get.mockResolvedValue({ data: { user: { id: 1 } } })
    const router = makeRouter()
    await router.push('/')
    expect(router.currentRoute.value.path).toBe('/')
  })
})
