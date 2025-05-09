import request from '../utils/request'

// 获取排行榜数据
export const getRankings = async ({ seasonId, page = 1, pageSize = 10 }) => {
  const { data } = await request({
    url: '/api/rankings',
    method: 'get',
    params: {
      season_id: seasonId,
      page,
      page_size: pageSize
    }
  })
  return {
    data: data.rankings.map(item => ({
      ...item,
      winRate: item.totalBattles > 0 
        ? Math.round((item.winCount / item.totalBattles) * 100) 
        : 0
    })),
    total: data.total
  }
}

// 获取赛季列表
export const getSeasons = async () => {
  const { data } = await request({
    url: '/api/v1/seasons',
    method: 'get'
  })
  return data
}

// 创建新赛季
export const createSeason = async (seasonData) => {
  const { data } = await request({
    url: '/api/seasons',
    method: 'post',
    data: {
      name: seasonData.name,
      start_time: seasonData.startTime.toISOString(),
      end_time: seasonData.endTime.toISOString()
    }
  })
  return data
}

// 获取用户排名详情
export const getUserRanking = async (userId) => {
  const { data } = await request({
    url: `/api/rankings/${userId}`,
    method: 'get'
  })
  return data
} 