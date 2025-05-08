// frontend/src/api/battle.js
import request from '@/utils/request'

export function getRandomPoetry(difficulty = 1) {
  return request({
    url: '/api/v1/battle/random-poetry',
    method: 'get',
    params: { difficulty }
  })
}

export function checkPoetryChain(poetry1, poetry2) {
  return request({
    url: '/api/v1/battle/check-chain',
    method: 'post',
    data: { poetry1, poetry2 }
  })
}

export function createBattle() {
  return request({
    url: '/api/v1/battle/create',  // 修改为正确的API路径
    method: 'post'
  })
}

export function updateBattle(battleId, data) {
  return request({
    url: `/api/v1/battle/${battleId}`,  // 修改为正确的API路径
    method: 'put',
    data
  })
}

export function getSeasonRankings(seasonId, limit = 10) {
  return request({
    url: '/api/v1/battle/season/rankings',
    method: 'get',
    params: { season_id: seasonId, limit }
  })
}