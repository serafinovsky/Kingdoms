import { useNavigate, useParams, useSearchParams, Navigate } from "@solidjs/router";
import { createSignal } from "solid-js";
import { authActions } from "../stores/authStore";
import axios, { AxiosError, AxiosResponse } from "axios";

interface AccessTokenResponse {
  access_token: string;
}

export default function Redirect() {
  const params = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = createSignal<"loading" | "success" | "error">("loading");

  const code = searchParams.code;
  const supportedPlatforms = ["github", "yandex"];

  if (!supportedPlatforms.includes(params.platform)) {
    return <Navigate href="/404" />;
  }

  if (!code) {
    return <Navigate href="/login" />;
  }

  axios
    .post(`/api/auth/${params.platform}/token/`, { code })
    .then((response: AxiosResponse<AccessTokenResponse>) => {
      const token = response.data;
      authActions.setAccessToken(token.access_token);
      setStatus("success");

      setTimeout(() => {
        navigate("/");
      }, 800); 
    })
    .catch((error: AxiosError) => {
      console.error(error.message);
      setStatus("error");
    });

  return (
    <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      {status() === "loading" && (
        <div class="w-24 h-24 border-4 border-blue-500 border-solid rounded-full border-t-transparent animate-spin"></div>
      )}
      {status() === "success" && (
        <div class="flex flex-col items-center text-emerald-600">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-28 h-28"
            viewBox="0 0 28 28"
            fill="currentColor"
          >
            <circle cx="12" cy="12" r="10" fill="currentColor" />
            <path
              d="M15.535 8.465a1 1 0 00-1.414 0L12 10.586l-2.121-2.121a1 1 0 10-1.414 1.414L10.586 12l-2.121 2.121a1 1 0 001.414 1.414L12 13.414l2.121 2.121a1 1 0 001.414-1.414L13.414 12l2.121-2.121a1 1 0 000-1.414z"
              fill="#fff"
            />
          </svg>
          <p class="mt-4 text-lg">Authorization successful!</p>
          <p class="mt-1 text-sm text-gray-500">Redirecting in 1 second...</p>
        </div>
      )}
      {status() === "error" && (
        <div class="flex flex-col items-center text-rose-600">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-28 h-28"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <circle cx="12" cy="12" r="10" fill="currentColor" />
            <path
              d="M16.192 7.808a1 1 0 0 0-1.414 0L12 10.586 9.222 7.808a1 1 0 0 0-1.414 1.414L10.586 12l-2.778 2.778a1 1 0 1 0 1.414 1.414L12 13.414l2.778 2.778a1 1 0 0 0 1.414-1.414L13.414 12l2.778-2.778a1 1 0 0 0 0-1.414z"
              fill="#fff"
            />
          </svg>
          <p class="mt-4 text-lg">Authorization failed, please try again.</p>
          <a href="/login" class="mt-2 text-blue-500 underline">
            Go back to the login page
          </a>
        </div>
      )}
    </div>
  );
}
