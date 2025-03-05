export const ErrorMessage = (props: { message: string }) => {
  return (
    <div class="w-full max-w-md mx-auto">
      <div class="p-4 bg-white/60 backdrop-blur-sm rounded-2xl shadow-xl
                  border border-white/10">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-amber-100/50 flex items-center justify-center
                      border border-amber-200/30 shadow-inner">
            <svg class="w-5 h-5 text-amber-600/70" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" 
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" 
                    clip-rule="evenodd"/>
            </svg>
          </div>
          <div class="flex-1">
            <p class="text-base font-medium text-gray-700">{props.message}</p>
          </div>
        </div>
      </div>
    </div>
  );
};