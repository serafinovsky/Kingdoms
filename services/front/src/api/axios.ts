import axios, { 
  AxiosError, 
  AxiosInstance, 
  AxiosResponse,
  InternalAxiosRequestConfig 
} from 'axios';
import { authStore, authActions } from '../stores/authStore';
import { BASE_URL } from '../config'

interface RefreshTokenResponse {
  access_token: string;
}

interface QueueItem {
  resolve: (value: unknown) => void;
  reject: (error: unknown) => void;
}

const API_BASE_URL = 'https://kingdoms-game.ru';
const AUTH_ENDPOINTS = {
  refresh: `${API_BASE_URL}/api/v1/auth/token/refresh/`,
};
const REQUEST_TIMEOUT = 10000;

class ApiClient {
  private api: AxiosInstance;
  private isRefreshing: boolean = false;
  private failedQueue: QueueItem[] = [];

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: REQUEST_TIMEOUT,
      withCredentials: true,
    });

    this.setupInterceptors();
  }

  private addToQueue(request: QueueItem): void {
    this.failedQueue.push(request);
  }

  private processQueue(error: AxiosError | null = null): void {
    this.failedQueue.forEach((request) => {
      if (error) {
        request.reject(error);
      } else {
        request.resolve(null);
      }
    });
    this.failedQueue = [];
  }

  private async refreshAuthToken(): Promise<string> {
    try {
      const { data } = await axios.post<RefreshTokenResponse>(
        AUTH_ENDPOINTS.refresh,
        {},
        { withCredentials: true }
      );
      
      const newToken = data.access_token;
      authActions.setAccessToken(newToken);
      return newToken;
    } catch (error) {
      authActions.clearAuth();
      throw error;
    }
  }

  private handleAuthError(error: AxiosError): Promise<unknown> {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (!originalRequest._retry) {
      originalRequest._retry = true;

      if (!this.isRefreshing) {
        this.isRefreshing = true;

        return this.refreshAuthToken()
          .then((newToken) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            this.api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
            this.processQueue();
            return this.api.request(originalRequest);
          })
          .catch((refreshError) => {
            this.processQueue(refreshError as AxiosError);
            authActions.clearAuth();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          })
          .finally(() => {
            this.isRefreshing = false;
          });
      }

      return new Promise((resolve, reject) => {
        this.addToQueue({
          resolve: () => {
            const currentToken = authStore.accessToken;
            if (originalRequest.headers && currentToken) {
              originalRequest.headers.Authorization = `Bearer ${currentToken}`;
            }
            resolve(this.api.request(originalRequest));
          },
          reject,
        });
      });
    }

    return Promise.reject(error);
  }

  private setupInterceptors(): void {
    this.api.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = authStore.accessToken;
        if (token) {
          this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401 && error.config) {
          return this.handleAuthError(error);
        }
        return Promise.reject(error);
      }
    );
  }

  public get client(): AxiosInstance {
    return this.api;
  }
}

export default new ApiClient().client;