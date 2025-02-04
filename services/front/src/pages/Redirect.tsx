import { useNavigate, useParams, useSearchParams, Navigate } from "@solidjs/router";
import { createSignal } from "solid-js";
import { authActions } from "../stores/authStore";
import axios, { AxiosError, AxiosResponse } from "axios";

interface AccessTokenResponse {
  access_token: string;
}

export default function Redirect() {
  const params = useParams();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = createSignal<"loading" | "success" | "error">("loading");
  const [countdown, setCountdown] = createSignal(1);

  const code = searchParams.code;
  const supportedPlatforms = ["github", "yandex"];

  if (!supportedPlatforms.includes(params.platform)) {
    return <Navigate href="/404" />;
  }

  if (!code) {
    return <Navigate href="/login" />;
  }

  axios
    .post(`/api/v1/auth/${params.platform}/token/`, { code })
    .then((response: AxiosResponse<AccessTokenResponse>) => {
      const token = response.data;
      authActions.setAccessToken(token.access_token);
      setStatus("success");

      setTimeout(() => {
        window.close();
      }, 1000);
    })
    .catch((error: AxiosError) => {
      console.error(error.message);
      setStatus("error");
    });

  return (
    <div class="min-h-screen flex items-center justify-center p-4">
      <div class="w-full max-w-md">
        <div class="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl 
                    border border-white/20 hover:shadow-2xl transition-all duration-300">
          {status() === "loading" && (
            <div class="flex flex-col items-center gap-4">
              <div class="w-8 h-8 border-4 border-sky-600/50 border-t-sky-600 
                          rounded-full animate-spin" />
              <p class="text-gray-600">Авторизация...</p>
            </div>
          )}

          {status() === "success" && (
            <div class="flex flex-col items-center gap-4 text-emerald-600">
              <div class="w-16 h-16 rounded-full bg-emerald-600/10 
                          flex items-center justify-center">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="w-8 h-8" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path 
                    fill-rule="evenodd" 
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                    clip-rule="evenodd" 
                  />
                </svg>
              </div>
              <div class="text-center">
                <p class="text-lg font-medium text-gray-800">
                  Авторизация успешна!
                </p>
                <p class="mt-1 text-sm text-gray-500">
                  Окно закроется автоматически через {countdown()} сек...
                </p>
              </div>
            </div>
          )}

          {status() === "error" && (
            <div class="flex flex-col items-center gap-4 text-red-600">
              <div class="w-16 h-16 rounded-full bg-red-600/10 
                          flex items-center justify-center">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="w-8 h-8" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path 
                    fill-rule="evenodd" 
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
                    clip-rule="evenodd" 
                  />
                </svg>
              </div>
              <div class="text-center">
                <p class="text-lg font-medium text-gray-800">
                  Ошибка авторизации
                </p>
                <p class="mt-1 text-sm text-gray-500">
                  Пожалуйста, попробуйте снова
                </p>
              </div>
              <button
                onClick={() => window.close()}
                class="mt-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-xl text-sm 
                       hover:bg-gray-200 active:scale-95 transition-all duration-150"
              >
                Закрыть окно
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}