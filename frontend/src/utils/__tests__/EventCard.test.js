import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// api / toast / navigation をモック
vi.mock('../../utils/api.js', () => {
  const get = vi.fn()
  const _delete = vi.fn()
  return {
    api: { get, delete: _delete },
    socket: { on(){}, off(){}, emit(){}, close(){} }
  }
})
vi.mock('../../utils/toast.js', () => ({ toast: vi.fn() }))
vi.mock('../../utils/navigation.js', () => ({ reloadPage: vi.fn() }))

import { api } from '../../utils/api.js'
import { toast } from '../../utils/toast.js'
import { reloadPage } from '../../utils/navigation.js'
import EventCard from '../../components/EventCard.vue'

const baseEvent = {
  id: 1,
  name: 'FLARE ミートアップ',
  start_at: new Date('2025-10-12T12:00:00Z').toISOString(),
  end_at: new Date('2025-10-12T13:00:00Z').toISOString(),
  created_by: 10,
  created_by_name: '主催者A',
  location: '会議室A',
  url: 'https://example.com',
  going: false
}

describe('EventCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // confirm は setup.js で true にスタブ
    api.get.mockResolvedValue({ data: { user: { id: 10, name: '主催者A' } } })
  })

  it('イベント情報が表示される', async () => {
    const wrapper = mount(EventCard, { props: { event: baseEvent } })
    await flushPromises()
    expect(wrapper.text()).toContain('FLARE ミートアップ')
    expect(wrapper.text()).toContain('主催: 主催者A')
    expect(wrapper.find('button.btn.btn-neutral').exists()).toBe(true)
  })

  it('削除→トースト→リロード', async () => {
    api.delete.mockResolvedValue({ data: { ok: true } })

    const wrapper = mount(EventCard, { props: { event: baseEvent } })
    await flushPromises()

    await wrapper.find('button.btn.btn-neutral').trigger('click')
    await flushPromises()

    expect(api.delete).toHaveBeenCalledWith(`/api/events/${baseEvent.id}`)
    expect(toast).toHaveBeenCalledWith('削除しました', 'success')
    expect(reloadPage).toHaveBeenCalled() // ← window.reload ではなく util を検証
  })

  it('削除失敗→エラートースト（リロードなし）', async () => {
    api.delete.mockRejectedValue(new Error('NG'))

    const wrapper = mount(EventCard, { props: { event: baseEvent } })
    await flushPromises()

    await wrapper.find('button.btn.btn-neutral').trigger('click').catch(() => {})
    await flushPromises()

    expect(toast).toHaveBeenCalledWith('削除に失敗しました', 'error')
    expect(reloadPage).not.toHaveBeenCalled()
  })

  it('作成者でない場合は削除ボタンが出ない', async () => {
    api.get.mockResolvedValueOnce({ data: { user: { id: 99, name: '他ユーザ' } } })
    const wrapper = mount(EventCard, { props: { event: baseEvent } })
    await flushPromises()
    expect(wrapper.find('button.btn.btn-neutral').exists()).toBe(false)
  })
})
