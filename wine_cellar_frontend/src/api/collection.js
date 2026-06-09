import request from '@/utils/request'

export function getWines(params) {
  return request({
    url: '/collection/wines/',
    method: 'get',
    params
  })
}

export function getWine(id) {
  return request({
    url: `/collection/wines/${id}/`,
    method: 'get'
  })
}

export function createWine(data) {
  return request({
    url: '/collection/wines/',
    method: 'post',
    data
  })
}

export function updateWine(id, data) {
  return request({
    url: `/collection/wines/${id}/`,
    method: 'put',
    data
  })
}

export function deleteWine(id) {
  return request({
    url: `/collection/wines/${id}/`,
    method: 'delete'
  })
}

export function valuateWine(id) {
  return request({
    url: `/collection/wines/${id}/valuate/`,
    method: 'post'
  })
}

export function getWineValuationHistory(id) {
  return request({
    url: `/collection/wines/${id}/valuation_history/`,
    method: 'get'
  })
}

export function searchWines(keyword) {
  return request({
    url: '/collection/wines/search/',
    method: 'get',
    params: { q: keyword }
  })
}

export function getCollectionOverview() {
  return request({
    url: '/collection/stats/overview/',
    method: 'get'
  })
}

export function getValuationTrend() {
  return request({
    url: '/collection/stats/valuation-trend/',
    method: 'get'
  })
}

export function getMaturityDistribution() {
  return request({
    url: '/collection/stats/maturity-distribution/',
    method: 'get'
  })
}
