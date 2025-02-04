import { createSignal, Show, JSX, onMount } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { authActions } from "../stores/authStore";
import { setUserStore } from "../stores/userStore";
import { UserMenu } from "../components/UserMenu";
import { Navbar } from "../components/Navbar";
import api from "../api/axios";

interface LayoutProps {
  children?: JSX.Element;
}

interface User {
  user_id: number;
  username: string;
  avatar: string;
}

const Layout = (props: LayoutProps) => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = createSignal<boolean>(false);
  const [isLoading, setIsLoading] = createSignal<boolean>(false);
  const [user, setUser] = createSignal<User>({
    user_id: -1,
    username: '',
    avatar: '',
  });

  onMount(async () => {
    try {
      const response = await api.get("/api/v1/users/me/", {
        withCredentials: true
      });
      setUser(response.data);
      setUserStore({user: response.data})
    } catch (error) {
      authActions.clearAuth();
      navigate("/login");
    } finally {
      setIsLoading(false);
    }
  });

  const handleClickOutside = (e: MouseEvent): void => {
    const target = e.target as HTMLElement;
    if (!target.closest('.user-menu')) {
      setIsMenuOpen(false);
    }
  };

  return (
    <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100" onClick={handleClickOutside}>
      <Navbar>
        <UserMenu 
          user={user()}
          isLoading={isLoading()}
          isMenuOpen={isMenuOpen()}
          onToggle={() => !isLoading() && setIsMenuOpen(!isMenuOpen())}
        />
      </Navbar>

      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {props.children}
      </main>
    </div>
  );
};

export default Layout;