import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/v1/poetry',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // 处理后端返回的错误
      const data = error.response.data;
      const message = data.message || data.detail || '请求失败';
      return Promise.reject(new Error(message));
    }
    return Promise.reject(error);
  }
);

// 获取诗词列表
export const getPoetryList = (params = {}) => {
  return api.get('/list', { params });
};

// 获取诗词详情
export const getPoetryDetail = (id) => {
  return api.get(`/${id}`);
};

// 获取收藏列表
export const getFavorites = () => {
  return api.get('/favorites');
};

// 收藏/取消收藏
export const toggleFavorite = (id) => {
  return api.post(`/${id}/favorite`);
}; 