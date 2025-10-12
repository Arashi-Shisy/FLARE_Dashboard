import { describe, it, expect, beforeEach } from 'vitest'

// 動的 import（ESM）
async function importToast() {
  const mod = await import('../../utils/toast.js')
  return mod.toast
}

describe('utils/toast', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('コンテナを生成し、トーストを追加後に自動消滅する', async () => {
    const toast = await importToast()
    toast('削除しました', 'success', 50)

    // コンテナが生成される（position: fixed のdiv）
    const container = Array.from(document.querySelectorAll('div'))
      .find(el => el.style && el.style.position === 'fixed')
    expect(container).toBeTruthy()

    // トースト要素が追加される
    const item = container.firstElementChild
    expect(item).toBeTruthy()
    expect(item.textContent).toContain('削除しました')

    // 自動消滅（CSSのfade-out待ちより長めに待機）
    await new Promise(res => setTimeout(res, 300))
    expect(container.firstElementChild).toBeNull()
  })
})
