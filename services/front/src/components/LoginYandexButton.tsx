import { JSX } from "solid-js";

type LoginButtonProps = {
  onClick: () => void;
  class?: string;
};

export const LoginYandexButton = (props: LoginButtonProps): JSX.Element => {
  return (
    <button
      onClick={props.onClick}
      type="button"
      class={`py-2 px-4 max-w-md flex justify-center items-center bg-gray-800 hover:bg-black focus:ring-bg-gray-700 focus:ring-offset-gray-600 text-white w-full transition ease-in duration-200 text-center text-base font-semibold shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 rounded-lg ${props.class || ''}`}
    >
      <svg class="mr-2" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="12" fill="#FC3F1D"/>
        <path d="M13.7695 6.72093H12.555C10.4731 6.72093 9.43215 7.7619 9.43215 9.32334C9.43215 11.0583 10.1261 11.9258 11.6876 12.9667L12.902 13.8342L9.43215 19.2125H6.65625L9.95264 14.3547C8.0442 12.9667 7.00324 11.7523 7.00324 9.49684C7.00324 6.72093 8.91167 4.8125 12.555 4.8125H16.1984V19.2125H13.7695V6.72093Z" fill="white"/>
      </svg>
      Войти через Yandex
    </button>
  );
};
