import { createStore } from 'solid-js/store';

interface AuthStore {
  accessToken: string | null;
  isAuthenticated: boolean;
}

const getInitialState = () => ({
  accessToken: null,
  isAuthenticated: localStorage.getItem('isAuthenticated') === 'true'
});

const [authStore, setAuthStore] = createStore<AuthStore>(getInitialState());

const authActions = {
  setAccessToken: (token: string | null) => {
    setAuthStore({ 
      accessToken: token,
      isAuthenticated: !!token
    });
    localStorage.setItem('isAuthenticated', !!token ? 'true' : 'false');
  },

  clearAuth: () => {
    setAuthStore({ 
      accessToken: null,
      isAuthenticated: false 
    });
    localStorage.removeItem('isAuthenticated');
  },

  getIsAuthenticated: () => localStorage.getItem('isAuthenticated') === 'true',
  
  getAccessToken: () => authStore.accessToken
};

export { authStore, authActions };