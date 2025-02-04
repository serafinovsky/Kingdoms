import { createStore } from 'solid-js/store';

interface User {
  user_id: number;
  username: string;
  avatar: string;
}

interface UserStore {
  user: User;
}

const getInitialState = () => ({
  user: {
    user_id: -1,
    username: '',
    avatar: '',
  },
});

const [userStore, setUserStore] = createStore<UserStore>(getInitialState());

export { userStore, setUserStore };