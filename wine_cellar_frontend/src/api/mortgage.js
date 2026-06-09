import request from '@/utils/request'

export function getApplications(params) {
  return request({
    url: '/mortgage/applications/',
    method: 'get',
    params
  })
}

export function getApplication(id) {
  return request({
    url: `/mortgage/applications/${id}/`,
    method: 'get'
  })
}

export function createApplication(data) {
  return request({
    url: '/mortgage/applications/',
    method: 'post',
    data
  })
}

export function updateApplication(id, data) {
  return request({
    url: `/mortgage/applications/${id}/`,
    method: 'put',
    data
  })
}

export function submitApplication(id) {
  return request({
    url: `/mortgage/applications/${id}/submit/`,
    method: 'post'
  })
}

export function startReview(id) {
  return request({
    url: `/mortgage/applications/${id}/start-review/`,
    method: 'post'
  })
}

export function approveApplication(id, data) {
  return request({
    url: `/mortgage/applications/${id}/approve/`,
    method: 'post',
    data
  })
}

export function rejectApplication(id, data) {
  return request({
    url: `/mortgage/applications/${id}/reject/`,
    method: 'post',
    data
  })
}

export function disburseApplication(id) {
  return request({
    url: `/mortgage/applications/${id}/disburse/`,
    method: 'post'
  })
}

export function addCollateral(id, data) {
  return request({
    url: `/mortgage/applications/${id}/add-collateral/`,
    method: 'post',
    data
  })
}

export function removeCollateral(id, data) {
  return request({
    url: `/mortgage/applications/${id}/remove-collateral/`,
    method: 'post',
    data
  })
}

export function getMortgageStats() {
  return request({
    url: '/mortgage/applications/stats/',
    method: 'get'
  })
}

export function releaseCollateral(id) {
  return request({
    url: `/mortgage/collaterals/${id}/release/`,
    method: 'post'
  })
}

export function recordPayment(id, data) {
  return request({
    url: `/mortgage/schedules/${id}/record-payment/`,
    method: 'post',
    data
  })
}
