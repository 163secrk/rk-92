import request from '@/utils/request'

export function login(username, password) {
  return request({
    url: '/auth/token/',
    method: 'post',
    data: { username, password }
  })
}

export function refreshToken(refresh) {
  return request({
    url: '/auth/token/refresh/',
    method: 'post',
    data: { refresh }
  })
}
