// リロードなどナビゲーション系の副作用ラッパ
export function reloadPage() {
  if (typeof window !== 'undefined' && window.location && typeof window.location.reload === 'function') {
    try {
      window.location.reload()
    } catch {
      // jsdom など未実装環境では何もしない
    }
  }
}
