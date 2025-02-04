import { JSX } from "solid-js";
import { A } from "@solidjs/router";
import logo from "../assets/logo.svg";

interface NavbarProps {
  children: JSX.Element;
}

export function Navbar(props: NavbarProps) {
  return (
    <nav class="bg-white/60 backdrop-blur-sm border-b border-gray-200/20 sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-4">
        <div class="flex justify-between h-16 items-center">
          <div class="flex-shrink-0">
            <A 
              href="/" 
              class="block hover:opacity-80 active:scale-95 transition-all duration-150"
            >
              <img src={logo} alt="Logo" style={{ height: '40px' }} />
            </A>
          </div>
          {props.children}
        </div>
      </div>
    </nav>
  );
}