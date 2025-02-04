export const ErrorMessage = (props: { message: string }) => {
  return (
    <div class="w-full max-w-md mx-auto">
      <div class="p-4 bg-white/60 backdrop-blur-sm rounded-2xl shadow-xl
                  border border-white/10 hover:shadow-2xl transition-all duration-300">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-red-100/50 flex items-center justify-center
                      border border-red-200/30 shadow-inner">
            <svg class="w-5 h-5 text-red-600/70" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" 
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" 
                    clip-rule="evenodd"/>
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-800/90">Ошибка соединения</h3>
            <p class="mt-1 text-sm text-gray-600/90">{props.message}</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            class="p-2 bg-white/70 rounded-xl hover:bg-white/90 active:scale-95
                   shadow-sm hover:shadow transition-all duration-200
                   flex items-center justify-center"
          >
            <svg class="w-5 h-5 text-gray-600/90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};