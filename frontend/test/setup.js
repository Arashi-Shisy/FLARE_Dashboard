// 共通セットアップ（jsdom環境）
// 1) Service Worker登録を無効化してエラー回避
Object.defineProperty(globalThis, 'navigator', {
  value: {
    ...globalThis.navigator,
    serviceWorker: { register: () => Promise.resolve() },
  },
  configurable: true,
})

// 2) window オブジェクトの最低限の用意
if (!globalThis.window) globalThis.window = {}

// 3) window.confirm は jsdom に実装があっても「未実装エラー」を投げるため、無条件で stub する
//    ※ テストごとに挙動を変えたい場合は、各テスト内で vi.spyOn(window, 'confirm').mockReturnValueOnce(false) などで上書きしてください
window.confirm = vi.fn(() => true)

// 4) Socket.IO クライアントをスタブ（接続しない）
vi.mock('socket.io-client', () => {
  return {
    io: () => ({
      on() {},
      off() {},
      emit() {},
      close() {}
    })
  }
})

// 5) axios をデフォルトでモックし、各テストで上書き可能に
import axios from 'axios'
vi.mock('axios', async () => {
  const real = await vi.importActual('axios')
  return {
    ...real,
    default: {
      create: () => ({
        get: vi.fn(),
        post: vi.fn(),
        delete: vi.fn()
      })
    }
  }
})
