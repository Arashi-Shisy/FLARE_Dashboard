// frontend/src/utils/api.js
import axios from 'axios'
import { io } from 'socket.io-client'

// API
export const api = axios.create({
  baseURL: '', // 同一オリジン前提
  withCredentials: true,
})

// Socket.IO
export const socket = io()

// 既存のブラウザ通知（必要に応じて使用）
export function notify(title, body) {
  try {
    if (Notification && Notification.permission === 'granted') {
      new Notification(title, { body })
    }
  } catch {}
}

// ★ DELETE時に確認モーダルを出すラッパー
const _delete = api.delete.bind(api)
api.delete = async function (url, ...args) {
  const mustConfirm =
    typeof url === 'string' &&
    (url.startsWith('/api/announcements/') ||
     url.startsWith('/api/chat/') ||
     url.startsWith('/api/events/'))
  if (mustConfirm) {
    const ok = window.confirm('削除しますか？')
    if (!ok) {
      // キャンセル時は例外でもreturnでもよい。ここでは例外にして呼び元で握り潰す想定。
      const err = new Error('CANCELLED_BY_USER')
      err.cancelled = true
      throw err
    }
  }
  return _delete(url, ...args)
}
