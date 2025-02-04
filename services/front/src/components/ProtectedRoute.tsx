import { Component, Show } from "solid-js";
import { Navigate } from "@solidjs/router";
import { createResource } from "solid-js";
import { authStore, authActions } from "../stores/authStore";
import axios from "axios";
import { LoadingSpinner } from "./LoadingSpinner";

interface ProtectedRouteProps {
  component: Component<{ children?: any }>;
}

const checkAuth = async () => {
  try {
    if (!authStore.accessToken && authStore.isAuthenticated) {
      const response = await axios.post(
        "/api/v1/auth/token/refresh/",
        {},
        { withCredentials: true }
      );
      authActions.setAccessToken(response.data.access_token);
      return true;
    }
    if (authStore.accessToken && authStore.isAuthenticated) {
      return true;
    }
    return false;
  } catch (error) {
    console.error("Failed to refresh token:", error);
    authActions.clearAuth();
    return false;
  }
};


const SkeletonLayout = () => (
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <nav class="bg-white/60 backdrop-blur-sm border-b border-gray-200/20 sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-4">
        <div class="flex justify-between h-16 items-center">
          <div class="flex-shrink-0">
            <div class="h-10 w-28 bg-gray-200 rounded-lg animate-pulse" />
          </div>
          <div class="h-10 w-10 rounded-xl bg-gray-200 animate-pulse" />
        </div>
      </div>
    </nav>
    <main class="max-w-4xl mx-auto px-4 py-8">
      <div class="space-y-4">
        <div class="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2].map(() => (
            <div class="bg-white/60 backdrop-blur-sm p-4 rounded-2xl h-64 animate-pulse">
              <div class="space-y-4">
                <div class="h-40 bg-gray-200 rounded-xl w-full" />
                <div class="h-4 bg-gray-200 rounded w-2/3" />
                <div class="h-4 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  </div>
);

const ProtectedRoute: Component<ProtectedRouteProps> = (props) => {
  const [isAuthorized] = createResource(checkAuth);

  return (
    <Show
      when={!isAuthorized.loading}
      fallback={<SkeletonLayout />}
    >
      <Show
        when={isAuthorized()}
        fallback={<Navigate href="/login" />}
      >
        <props.component />
      </Show>
    </Show>
  );
};

export default ProtectedRoute;