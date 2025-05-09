// frontend/src/api/battle.js
import request from '@/utils/request'

export function getRandomPoetry(difficulty = 1) {
  return request({
    url: '/api/v1/battle/random-poetry', // This endpoint might be deprecated if not used by new game logic
    method: 'get',
    params: { difficulty }
  })
}

export function checkPoetryChain(poetry1, poetry2) {
  return request({
    url: '/api/v1/battle/check-chain', // This endpoint might be deprecated if not used by new game logic
    method: 'post',
    data: { poetry1, poetry2 }
  })
}

// Removed old createBattle() function, use startNewBattle(battleType) instead
// export function createBattle() {
//   return request({
//     url: '/api/v1/battle/create', 
//     method: 'post'
//   })
// }

// Starts a new battle of a specific type
export function startNewBattle(battleType) {
  return request({
    url: '/api/v1/battles/start',
    method: 'post',
    data: { battle_type: battleType }
  })
}

// Submits an answer for an ongoing battle
export function submitBattleAnswer(battleId, answer) {
  return request({
    url: `/api/v1/battles/${battleId}/submit`,
    method: 'post',
    data: { answer: answer }
  })
}

// General update for a battle (if still needed, distinct from submitting an answer)
export function updateBattle(battleId, data) {
  return request({
    url: `/api/v1/battles/${battleId}`,
    method: 'put',
    data
  })
}

export function getSeasonRankings(seasonId, limit = 10) {
  return request({
    url: '/api/v1/rankings',
    method: 'get',
    params: { season: seasonId, pageSize: limit }
  })
}