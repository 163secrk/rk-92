import request from '@/utils/request'

export function getCustomers(params) {
  return request({
    url: '/sales/customers/',
    method: 'get',
    params
  })
}

export function getCustomer(id) {
  return request({
    url: `/sales/customers/${id}/`,
    method: 'get'
  })
}

export function createCustomer(data) {
  return request({
    url: '/sales/customers/',
    method: 'post',
    data
  })
}

export function updateCustomer(id, data) {
  return request({
    url: `/sales/customers/${id}/`,
    method: 'put',
    data
  })
}

export function deleteCustomer(id) {
  return request({
    url: `/sales/customers/${id}/`,
    method: 'delete'
  })
}

export function searchCustomers(keyword) {
  return request({
    url: '/sales/customers/search/',
    method: 'get',
    params: { q: keyword }
  })
}

export function getOrders(params) {
  return request({
    url: '/sales/orders/',
    method: 'get',
    params
  })
}

export function getOrder(id) {
  return request({
    url: `/sales/orders/${id}/`,
    method: 'get'
  })
}

export function createOrder(data) {
  return request({
    url: '/sales/orders/',
    method: 'post',
    data
  })
}

export function updateOrder(id, data) {
  return request({
    url: `/sales/orders/${id}/`,
    method: 'put',
    data
  })
}

export function deleteOrder(id) {
  return request({
    url: `/sales/orders/${id}/`,
    method: 'delete'
  })
}

export function confirmOrder(id) {
  return request({
    url: `/sales/orders/${id}/confirm/`,
    method: 'post'
  })
}

export function cancelOrder(id) {
  return request({
    url: `/sales/orders/${id}/cancel/`,
    method: 'post'
  })
}

export function shipOrder(id, data) {
  return request({
    url: `/sales/orders/${id}/ship/`,
    method: 'post',
    data
  })
}

export function completeOrder(id) {
  return request({
    url: `/sales/orders/${id}/complete/`,
    method: 'post'
  })
}

export function getAuctions(params) {
  return request({
    url: '/sales/auctions/',
    method: 'get',
    params
  })
}

export function getAuction(id) {
  return request({
    url: `/sales/auctions/${id}/`,
    method: 'get'
  })
}

export function createAuction(data) {
  return request({
    url: '/sales/auctions/',
    method: 'post',
    data
  })
}

export function updateAuction(id, data) {
  return request({
    url: `/sales/auctions/${id}/`,
    method: 'put',
    data
  })
}

export function deleteAuction(id) {
  return request({
    url: `/sales/auctions/${id}/`,
    method: 'delete'
  })
}

export function startAuction(id) {
  return request({
    url: `/sales/auctions/${id}/start/`,
    method: 'post'
  })
}

export function endAuction(id) {
  return request({
    url: `/sales/auctions/${id}/end/`,
    method: 'post'
  })
}

export function placeBid(id, data) {
  return request({
    url: `/sales/auctions/${id}/place_bid/`,
    method: 'post',
    data
  })
}

export function getBidHistory(id) {
  return request({
    url: `/sales/auctions/${id}/bid_history/`,
    method: 'get'
  })
}

export function getSalesOverview() {
  return request({
    url: '/sales/stats/overview/',
    method: 'get'
  })
}
