// import { createStore } from 'solid-js/store';

// interface AuthStore {
//   accessToken: string | null;
// }

// const [authStore, setAuthStore] = createStore<AuthStore>({
//   accessToken: null,
// });

// const authActions = {
//   setAccessToken: (token: string | null) => {
//     setAuthStore({ accessToken: token });
//   },

//   clearAuth: () => {
//     setAuthStore({ accessToken: null });
//   },

//   isAuthenticated: () => !!authStore.accessToken,
// };

// export { authStore, authActions };


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

  getIsAuthenticated: () => authStore.isAuthenticated,
  
  getAccessToken: () => authStore.accessToken
};

export { authStore, authActions };