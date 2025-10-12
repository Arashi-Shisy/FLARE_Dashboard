import axios from 'axios'
import { io } from 'socket.io-client'

export const api = axios.create({
  baseURL: '',
  withCredentials: true
})

export const socket = io('/', { path: '/socket.io' })

export async function notify(title, body){
  if (!('Notification' in window)) return
  const permission = await Notification.requestPermission()
  if (permission !== 'granted') return
  // show via service worker if registered
  const reg = await navigator.serviceWorker.getRegistration()
  if (reg) {
    reg.active?.postMessage({ type:'SHOW_NOTIFICATION', title, body })
  } else {
    new Notification(title, { body })
  }
}
