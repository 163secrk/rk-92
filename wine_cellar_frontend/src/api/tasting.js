import request from '@/utils/request'

export function getTastingEvents(params) {
  return request({
    url: '/tasting/events/',
    method: 'get',
    params
  })
}

export function getTastingEvent(id) {
  return request({
    url: `/tasting/events/${id}/`,
    method: 'get'
  })
}

export function createTastingEvent(data) {
  return request({
    url: '/tasting/events/',
    method: 'post',
    data
  })
}

export function updateTastingEvent(id, data) {
  return request({
    url: `/tasting/events/${id}/`,
    method: 'put',
    data
  })
}

export function deleteTastingEvent(id) {
  return request({
    url: `/tasting/events/${id}/`,
    method: 'delete'
  })
}

export function checkInEvent(id, data) {
  return request({
    url: `/tasting/events/${id}/check_in/`,
    method: 'post',
    data
  })
}

export function registerEvent(id, data) {
  return request({
    url: `/tasting/events/${id}/register/`,
    method: 'post',
    data
  })
}

export function getEventAttendees(id, params) {
  return request({
    url: `/tasting/events/${id}/attendees/`,
    method: 'get',
    params
  })
}

export function getEventNotes(id) {
  return request({
    url: `/tasting/events/${id}/notes/`,
    method: 'get'
  })
}

export function getEventStats(id) {
  return request({
    url: `/tasting/events/${id}/stats/`,
    method: 'get'
  })
}

export function getTastingAttendees(params) {
  return request({
    url: '/tasting/attendees/',
    method: 'get',
    params
  })
}

export function getTastingAttendee(id) {
  return request({
    url: `/tasting/attendees/${id}/`,
    method: 'get'
  })
}

export function checkInAttendee(id) {
  return request({
    url: `/tasting/attendees/${id}/check_in/`,
    method: 'post'
  })
}

export function getTastingNotes(params) {
  return request({
    url: '/tasting/notes/',
    method: 'get',
    params
  })
}

export function getTastingNote(id) {
  return request({
    url: `/tasting/notes/${id}/`,
    method: 'get'
  })
}

export function createTastingNote(data) {
  return request({
    url: '/tasting/notes/',
    method: 'post',
    data
  })
}

export function updateTastingNote(id, data) {
  return request({
    url: `/tasting/notes/${id}/`,
    method: 'put',
    data
  })
}

export function deleteTastingNote(id) {
  return request({
    url: `/tasting/notes/${id}/`,
    method: 'delete'
  })
}

export function getTastingOverview() {
  return request({
    url: '/tasting/stats/overview/',
    method: 'get'
  })
}
