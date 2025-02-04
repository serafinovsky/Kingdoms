import "../index.css";

import { LoginGithubButton } from "../components/LoginGithubButton"
import { LoginYandexButton } from "../components/LoginYandexButton"
import { useNavigate } from "@solidjs/router"
import { authActions } from '../stores/authStore';


export default function Login() {
  const openAuthWindow = (url: string) => {
    authActions.clearAuth();
    const width = 600;
    const height = 700;
    const left = window.screenX + (window.outerWidth - width) / 2;
    const top = window.screenY + (window.outerHeight - height) / 2;

    const authWindow = window.open(
      url,
      'Auth',
      `width=${width},height=${height},left=${left},top=${top},popup=1`
    );

    if (authWindow) {
      const checkAuth = setInterval(() => {
        try {
          if (authWindow.closed) {
            clearInterval(checkAuth);
            const isAuthenticated = authActions.getIsAuthenticated();
            if (isAuthenticated) {
              window.location.href = '/';
            }
          }
        } catch (e) {
          clearInterval(checkAuth);
        }
      }, 500);
    }
  };

  const handleGithubLogin = () => {
    openAuthWindow('http://localhost:8889/api/v1/auth/github/authorize/');
  };
  
  const handleYandexLogin = () => {
    openAuthWindow('http://localhost:8889/api/v1/auth/yandex/authorize/');
  };

  return (
    <div class="min-h-screen flex items-center justify-center p-4">
      <div class="w-full max-w-md">
        <div class="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl 
                    border border-white/20 hover:shadow-2xl transition-all duration-300">
          <h2 class="text-2xl font-bold text-gray-800/90 mb-8 text-center">
            Войти в игру
          </h2>
          
          <div class="space-y-4">
            <LoginGithubButton 
              onClick={handleGithubLogin} 
              class="w-full py-3 px-4 flex items-center justify-center gap-3 
                     bg-gray-800/90 text-white rounded-xl text-sm font-medium
                     shadow-lg shadow-gray-800/10 hover:bg-opacity-80 
                     active:scale-[0.98] transition-all duration-300 backdrop-blur-sm"
            />
            <LoginYandexButton 
              onClick={handleYandexLogin} 
              class="w-full py-3 px-4 flex items-center justify-center gap-3
                     bg-[#fc3f1d]/90 text-white rounded-xl text-sm font-medium
                     shadow-lg shadow-[#fc3f1d]/10 hover:bg-opacity-80
                     active:scale-[0.98] transition-all duration-300 backdrop-blur-sm"
            />
          </div>
        </div>
      </div>
    </div>
  );
}