/**
 * CodeForge IDE - Core API Client
 */

class ApiClient {
  static getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  static getCsrfToken() {
    let token = ApiClient.getCookie('csrftoken');
    if (!token) {
      const csrfInput = document.querySelector('input[name=csrfmiddlewaretoken]');
      if (csrfInput && csrfInput.value) {
        token = csrfInput.value;
      }
    }
    if (!token) {
      const metaTag = document.querySelector('meta[name="csrf-token"]');
      if (metaTag && metaTag.content) {
        token = metaTag.content;
      }
    }
    return token || '';
  }

  static getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'X-CSRFToken': ApiClient.getCsrfToken()
    };
    const token = localStorage.getItem('codeforge_token');
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }
    return headers;
  }

  static async request(url, options = {}) {
    const config = {
      method: options.method || 'GET',
      headers: {
        ...ApiClient.getHeaders(),
        ...(options.headers || {})
      },
      ...options
    };

    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, config);
      if (response.status === 204) return null;

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const errorMsg = data.detail || data.error || data.message || Object.values(data)[0] || `Request failed with status ${response.status}`;
        throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      }
      return data;
    } catch (error) {
      console.error(`API Error [${options.method || 'GET'} ${url}]:`, error);
      throw error;
    }
  }

  static get(url, params = {}) {
    const query = new URLSearchParams(params).toString();
    const fullUrl = query ? `${url}?${query}` : url;
    return ApiClient.request(fullUrl, { method: 'GET' });
  }

  static post(url, body = {}) {
    return ApiClient.request(url, { method: 'POST', body });
  }

  static put(url, body = {}) {
    return ApiClient.request(url, { method: 'PUT', body });
  }

  static patch(url, body = {}) {
    return ApiClient.request(url, { method: 'PATCH', body });
  }

  static delete(url) {
    return ApiClient.request(url, { method: 'DELETE' });
  }
}

window.ApiClient = ApiClient;
