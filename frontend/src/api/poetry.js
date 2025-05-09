import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/poetry',
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
    if (error.response && error.response.data) {
      const data = error.response.data;
      let detailedMessage = '请求处理失败'; // Default message

      if (Array.isArray(data.detail)) {
        // Format FastAPI validation errors array
        detailedMessage = data.detail.map(err => {
          const field = err.loc && err.loc.length > 1 ? err.loc[1] : (err.loc ? err.loc.join('.') : 'field');
          return `${field}: ${err.msg}`;
        }).join('; ');
      } else if (typeof data.detail === 'string') {
        detailedMessage = data.detail;
      } else if (typeof data.message === 'string') {
        detailedMessage = data.message;
      }

      console.error("Backend Error Data:", data); // Log the original error data from backend
      return Promise.reject(new Error(detailedMessage));
    } else if (error.message) {
      return Promise.reject(new Error(error.message));
    }
    return Promise.reject(new Error('网络请求错误'));
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

// Removed getFavorites and toggleFavorite functions
// // 获取收藏列表
// export const getFavorites = () => {
//   return api.get('/favorites');
// };

// // 收藏/取消收藏
// export const toggleFavorite = (id) => {
//   return api.post(`/${id}/favorite`);
// }; 