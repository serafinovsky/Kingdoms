// ProtectedRoute.tsx
import { Component, createSignal, onMount, Show } from "solid-js";
import { Navigate } from "@solidjs/router";
import { authStore, authActions } from "../stores/authStore";
import axios from "axios";
import LoadingSpinner from "./LoadingSpinner";

interface ProtectedRouteProps {
  component: Component<{ children?: any }>;
}

const ProtectedRoute: Component<ProtectedRouteProps> = (props) => {
  const [isLoading, setIsLoading] = createSignal(true);
  const [isAuthorized, setIsAuthorized] = createSignal(false);

  onMount(async () => {
    if (!authStore.accessToken && authStore.isAuthenticated) {
      try {
        const response = await axios.post("/api/auth/token/refresh/", {}, { 
          withCredentials: true 
        });
        authActions.setAccessToken(response.data.access_token);
        setIsAuthorized(true);
      } catch (error) {
        console.error("Failed to refresh token:", error);
        authActions.clearAuth();
        setIsAuthorized(false);
      }
    } else {
      setIsAuthorized(authStore.isAuthenticated);
    }
    setIsLoading(false);
  });

  return (
    <Show
      when={!isLoading()}
      fallback={<LoadingSpinner/>}
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