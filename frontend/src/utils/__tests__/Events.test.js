import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../utils/api.js', () => {
  const get = vi.fn()
  const post = vi.fn()
  return {
    api: { get, post },
    socket: { on(){}, off(){}, emit(){}, close(){} }
  }
})
vi.mock('../../utils/toast.js', () => ({ toast: vi.fn() }))

import { api } from '../../utils/api.js'
// ★ ここが修正ポイント：pages への相対パス
import Events from '../../pages/Events.vue'

describe('Events page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('0件なら空メッセージ', async () => {
    api.get.mockResolvedValue({ data: { items: [] } })
    const wrapper = mount(Events)
    await flushPromises()
    expect(wrapper.text()).toContain('イベントはまだありません')
  })

  it('一覧を描画', async () => {
    api.get.mockResolvedValue({
      data: {
        items: [
          { id:1, name:'A', start_at:new Date().toISOString(), end_at:new Date().toISOString(), created_by:1 },
          { id:2, name:'B', start_at:new Date().toISOString(), end_at:new Date().toISOString(), created_by:2 }
        ]
      }
    })
    const wrapper = mount(Events)
    await flushPromises()
    expect(wrapper.text()).toContain('A')
    expect(wrapper.text()).toContain('B')
    // EventCard が2つ以上レンダされていることをゆるく検証
    expect(wrapper.findAll('.event-card').length >= 2).toBe(true)
  })
})
