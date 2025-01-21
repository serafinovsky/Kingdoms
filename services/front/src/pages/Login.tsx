import "../index.css";

import { LoginGithubButton } from "../components/LoginGithubButton"
import { LoginYandexButton } from "../components/LoginYandexButton"

export default function Login() {
  const handleGithubLogin = () => {
    window.location.href = 'http://localhost:8889/api/auth/github/authorize/';
  };
  const handleYandexLogin = () => {
    window.location.href = 'http://localhost:8889/api/auth/yandex/authorize/';
  };

  return (
    <div class="container flex items-center h-screen bg-gray-100">
      <div class="mx-auto">
          <LoginGithubButton 
            onClick={handleGithubLogin} 
            class="mb-2"
          />
          <LoginYandexButton 
            onClick={handleYandexLogin} 
          />
      </div>
    </div>
  );
}
