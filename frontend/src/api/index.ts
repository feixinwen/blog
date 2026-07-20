import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',  // 后端地址
  timeout: 10000,
})

// 请求拦截器：自动带 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：401 时清除过期 token
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // 如果不在登录页，跳转登录页
      if (!window.location.pathname.includes('/admin/login')) {
        window.location.href = '/admin/login'
      }
    }
    return Promise.reject(error)
  },
)

// ==================== 类型定义 ====================

export interface ArticleListItem {
  id: number
  title: string
  slug: string
  summary: string | null
  cover_url: string | null
  category_name: string | null
  category_slug: string | null
  created_at: string
}

export interface ArticleDetail {
  id: number
  title: string
  slug: string
  content: string
  summary: string | null
  cover_url: string | null
  category_name: string | null
  category_slug: string | null
  created_at: string
  updated_at: string
}

export interface ArticleAdminDetail {
  id: number
  title: string
  slug: string
  content: string
  summary: string | null
  cover_url: string | null
  category_id: number | null
  category_name: string | null
  tag_ids: number[]
  is_published: boolean
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface Category {
  id: number
  name: string
  slug: string
  article_count: number
}

export interface Tag {
  id: number
  name: string
  slug: string
  article_count: number
}

export interface Comment {
  id: number
  article_id: number
  author_name: string
  content: string
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

// ==================== API 函数 ====================

// 公开接口
export const fetchArticles = (
  page = 1,
  pageSize = 10,
  categorySlug?: string,
  tagSlug?: string,
) =>
  api.get<PaginatedResponse<ArticleListItem>>('/api/articles', {
    params: { page, page_size: pageSize, category_slug: categorySlug, tag_slug: tagSlug },
  })

export const fetchArticle = (slug: string) =>
  api.get<ArticleDetail>(`/api/articles/${slug}`)

export const fetchCategories = () =>
  api.get<Category[]>('/api/categories')

export const fetchTags = () =>
  api.get<Tag[]>('/api/tags')

export const fetchComments = (articleId: number) =>
  api.get<Comment[]>('/api/comments', { params: { article_id: articleId } })

export const createComment = (data: {
  article_id: number
  author_name: string
  author_email: string
  content: string
}) => api.post<Comment>('/api/comments', data)

// 后台接口
export const login = (username: string, password: string) =>
  api.post<LoginResponse>('/api/admin/login', { username, password })

export const fetchAdminArticles = () =>
  api.get<ArticleDetail[]>('/api/admin/articles')

export const fetchAdminArticle = (id: number) =>
  api.get<ArticleAdminDetail>(`/api/admin/articles/${id}`)

export const createArticle = (data: any) =>
  api.post<ArticleDetail>('/api/admin/articles', data)

export const updateArticle = (id: number, data: any) =>
  api.put<ArticleDetail>(`/api/admin/articles/${id}`, data)

export const deleteArticle = (id: number) =>
  api.delete(`/api/admin/articles/${id}`)

export const fetchAdminCategories = () =>
  api.get<Category[]>('/api/admin/categories')

export const createCategory = (data: { name: string; slug: string }) =>
  api.post<Category>('/api/admin/categories', data)

export const updateCategory = (id: number, data: { name?: string; slug?: string }) =>
  api.put<Category>(`/api/admin/categories/${id}`, data)

export const deleteCategory = (id: number) =>
  api.delete(`/api/admin/categories/${id}`)

export const fetchAdminTags = () =>
  api.get<Tag[]>('/api/admin/tags')

export const createTag = (data: { name: string; slug: string }) =>
  api.post<Tag>('/api/admin/tags', data)

export const updateTag = (id: number, data: { name?: string; slug?: string }) =>
  api.put<Tag>(`/api/admin/tags/${id}`, data)

export const deleteTag = (id: number) =>
  api.delete(`/api/admin/tags/${id}`)

export const fetchAdminComments = () =>
  api.get<Comment[]>('/api/admin/comments')

export const deleteComment = (id: number) =>
  api.delete(`/api/admin/comments/${id}`)

export const uploadImage = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<{ url: string }>('/api/admin/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
