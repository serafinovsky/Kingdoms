import { A } from "@solidjs/router";

export default function NotFound() {
  return (
    <div class="min-h-screen flex items-center justify-center">
      <div class="bg-white/60 backdrop-blur-sm p-12 rounded-2xl shadow-xl max-w-lg
                  border border-white/10 hover:shadow-2xl transition-all duration-300">
        <div class="flex flex-col items-center space-y-6">
          <div class="w-24 h-24 rounded-2xl bg-sky-100/50 flex items-center justify-center
                      border border-sky-200/30 shadow-inner">
            <svg class="w-12 h-12 text-sky-700/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="text-center space-y-2">
            <h1 class="text-4xl font-bold text-gray-800/90">Страница не найдена</h1>
            <p class="text-gray-600/90">Возможно, она была удалена или перемещена</p>
          </div>
          <A
            href="/"
            class="px-6 py-2.5 bg-sky-700/70 text-white rounded-xl text-sm 
                   font-medium shadow-lg shadow-sky-700/10 hover:bg-opacity-80 
                   active:scale-[0.98] transition-all duration-300 backdrop-blur-sm"
          >
            Вернуться на главную
          </A>
        </div>
      </div>
    </div>
  );
}