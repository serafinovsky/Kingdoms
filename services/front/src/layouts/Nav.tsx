import { createSignal, Show, JSX, onMount } from "solid-js";
import { useNavigate } from "@solidjs/router";
import logo from "../assets/logo.svg";
import fallback_avatar from "../assets/fallback_avatar.svg";
import { authActions } from "../stores/authStore";
import axios from "axios";
import api from "../api/axios";

interface LayoutProps {
  children?: JSX.Element;
}

export interface User {
  username: string;
  avatar: string;
}

const Layout = (props: LayoutProps) => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = createSignal<boolean>(false);
  const [isLoading, setIsLoading] = createSignal<boolean>(true);
  const [user, setUser] = createSignal<User>({
    username: '',
    avatar: '',
  });

  onMount(async () => {
    try {
      const response = await api.get("/api/users/me/", {
        withCredentials: true
      });
      setUser(response.data);
    } catch (error) {
      authActions.clearAuth();
      navigate("/login");
    } finally {
      setIsLoading(false);
    }
  });

  const toggleMenu = (): void => {
    if (!isLoading()) {
      setIsMenuOpen(!isMenuOpen());
    }
  };

  const handleClickOutside = (e: MouseEvent): void => {
    const target = e.target as HTMLElement;
    if (!target.closest('.user-menu')) {
      setIsMenuOpen(false);
    }
  };

  return (
    <div class="min-h-screen" onClick={handleClickOutside}>
      <nav>
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16 items-center">
            <div class="flex-shrink-0">
              <img src={logo} alt="Logo" style={{ height: '44px' }} />
            </div>

            <div class="relative user-menu">
              <button
                onClick={toggleMenu}
                class={`flex items-center focus:outline-none ${
                  isLoading() ? 'cursor-wait opacity-50' : ''
                }`}
                disabled={isLoading()}
                aria-label="User menu"
                aria-expanded={isMenuOpen()}
              >
                <div class={`relative h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden ${
                  !isLoading() ? 'hover:ring-2 hover:ring-gray-300' : ''
                } transition-all duration-200`}>
                  <Show
                    when={!isLoading()}
                    fallback={
                      <div class="animate-pulse w-full h-full bg-gray-300" />
                    }
                  >
                    <img
                      src={user().avatar}
                      alt="User avatar"
                      class="object-cover"
                      onError={(e: Event) => {
                        const target = e.currentTarget as HTMLImageElement;
                        target.src = fallback_avatar;
                        target.width = 20;
                      }}
                    />
                  </Show>
                </div>
              </button>

              <Show when={isMenuOpen() && !isLoading()}>
                <div 
                  class="absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 z-50 transition-all duration-200 ease-out"
                  role="menu"
                  aria-orientation="vertical"
                >
                  <div class="px-4 py-2 border-b border-gray-100">
                    <p class="text-sm text-gray-700">Signed in as</p>
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {user().username}
                    </p>
                  </div>
                  
                  <MenuLink href="/profile" text="Your Profile" />
                  <MenuLink href="/games" text="Game history" />
                  
                  <button
                    onClick={async () => {
                      try {
                        const response = await axios.post("/api/auth/token/revoke/", {}, { 
                          withCredentials: true 
                        });
                        authActions.clearAuth();
                        navigate("/login");
                      } catch (error) {
                        console.error("Failed to refresh token:", error);
                        alert('Something wrong! Try again later')
                      }
                    }}
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 transition-colors duration-150"
                    role="menuitem"
                  >
                    Sign out
                  </button>
                </div>
              </Show>
            </div>
          </div>
        </div>
      </nav>

      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {props.children}
      </main>
    </div>
  );
};


interface MenuLinkProps {
  href: string;
  text: string;
}


const MenuLink = (props: MenuLinkProps) => {
  return (
    <a
      href={props.href}
      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-150"
      role="menuitem"
    >
      {props.text}
    </a>
  );
};

export default Layout;