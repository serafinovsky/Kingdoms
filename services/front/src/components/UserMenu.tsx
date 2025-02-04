import { Show } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { authActions } from "../stores/authStore";
import fallback_avatar from "../assets/fallback_avatar.svg";
import axios from "axios";

interface User {
  username: string;
  avatar: string;
}

interface UserMenuProps {
  user: User;
  isLoading: boolean;
  isMenuOpen: boolean;
  onToggle: () => void;
}

interface MenuLinkProps {
  href: string;
  text: string;
}

const MenuLink = (props: MenuLinkProps) => {
  return (
    <a
      href={props.href}
      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50/50 
             transition-colors duration-150"
      role="menuitem"
    >
      {props.text}
    </a>
  );
};

export function UserMenu(props: UserMenuProps) {
  const navigate = useNavigate();

  return (
    <div class="relative user-menu">
      <button
        onClick={props.onToggle}
        class={`flex items-center focus:outline-none ${
          props.isLoading ? 'cursor-wait opacity-50' : ''
        }`}
        disabled={props.isLoading}
        aria-label="User menu"
        aria-expanded={props.isMenuOpen}
      >
      <div class={`relative h-10 w-10 rounded-xl bg-gray-100 flex items-center justify-center 
                  overflow-hidden shadow-lg ${
                    !props.isLoading ? 'hover:shadow-xl hover:scale-105' : ''
                  } transition-all duration-200`}>
        <Show
          when={!props.isLoading}
          fallback={<div class="animate-pulse w-full h-full bg-gray-200" />}
        >
          <img
            src={props.user.avatar}
            alt="User avatar"
            class="w-full h-full object-cover"
            onError={(e: Event) => {
              const target = e.currentTarget as HTMLImageElement;
              target.src = fallback_avatar;
              target.width = 20;
            }}
          />
        </Show>
      </div>
      </button>

      <Show when={props.isMenuOpen && !props.isLoading}>
        <div 
          class="absolute right-0 mt-2 w-48 rounded-xl shadow-xl py-1 bg-white/80 
                 backdrop-blur-sm border border-white/20 z-50 
                 transition-all duration-200 ease-out"
          role="menu"
          aria-orientation="vertical"
        >
          <div class="px-4 py-2 border-b border-gray-100/20">
            <p class="text-sm text-gray-600">Вы вошли как</p>
            <p class="text-sm font-medium text-gray-900 truncate">
              {props.user.username}
            </p>
          </div>
          
          <MenuLink href="/profile" text="Профиль" />
          <MenuLink href="/games" text="История игр" />
          
          <button
            onClick={async () => {
              try {
                await axios.post("/api/v1/auth/token/revoke/", {}, { 
                  withCredentials: true 
                });
                authActions.clearAuth();
                navigate("/login");
              } catch (error) {
                console.error("Failed to refresh token:", error);
                alert('Что-то пошло не так! Попробуйте позже')
              }
            }}
            class="block w-full text-left px-4 py-2 text-sm text-red-600 
                   hover:bg-red-50/50 transition-colors duration-150"
            role="menuitem"
          >
            Выйти
          </button>
        </div>
      </Show>
    </div>
  );
}