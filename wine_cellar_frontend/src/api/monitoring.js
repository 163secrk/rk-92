import request from '@/utils/request'

export function getCellars() {
  return request({
    url: '/monitoring/cellars/',
    method: 'get'
  })
}

export function getCellar(id) {
  return request({
    url: `/monitoring/cellars/${id}/`,
    method: 'get'
  })
}

export function getCellarStatus(id) {
  return request({
    url: `/monitoring/cellars/${id}/current_status/`,
    method: 'get'
  })
}

export function getCellarHistory(id, hours = 24) {
  return request({
    url: `/monitoring/cellars/${id}/history/`,
    method: 'get',
    params: { hours }
  })
}

export function simulateReading(id) {
  return request({
    url: `/monitoring/cellars/${id}/simulate_reading/`,
    method: 'post'
  })
}

export function getReadings(params) {
  return request({
    url: '/monitoring/readings/',
    method: 'get',
    params
  })
}

export function getAlerts(params) {
  return request({
    url: '/monitoring/alerts/',
    method: 'get',
    params
  })
}

export function getActiveAlerts() {
  return request({
    url: '/monitoring/alerts/active/',
    method: 'get'
  })
}

export function getAlertStats() {
  return request({
    url: '/monitoring/alerts/stats/',
    method: 'get'
  })
}

export function acknowledgeAlert(id) {
  return request({
    url: `/monitoring/alerts/${id}/acknowledge/`,
    method: 'post'
  })
}

export function resolveAlert(id) {
  return request({
    url: `/monitoring/alerts/${id}/resolve/`,
    method: 'post'
  })
}
