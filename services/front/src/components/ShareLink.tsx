import { createSignal } from 'solid-js';

export const ShareLink = () => {
  const [copied, setCopied] = createSignal(false);
  const baseUrl = window.location.origin;
  const link = window.location.href;

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div class="mb-8 w-full max-w-2xl mx-auto">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">Пригласить игроков</h2>
      <div class="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-xl 
                  border border-white/20 hover:shadow-2xl transition-all duration-300">
        <div class="flex flex-col gap-4">
          <div class="flex items-center gap-3 bg-gray-50/50 px-4 py-3 rounded-xl 
                      border border-gray-100/20 backdrop-blur-md">
            <svg class="w-5 h-5 text-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <input
              type="text"
              readonly
              value={link}
              class="flex-1 bg-transparent text-gray-700 text-sm focus:outline-none 
                     selection:bg-sky-100 font-medium w-full"
            />
          </div>

          <button
            onClick={copyToClipboard}
            class={`w-full px-4 py-3 rounded-xl text-sm font-medium flex items-center 
                   justify-center gap-2 transition-all duration-300 shadow-lg
                   ${copied() 
                     ? 'bg-emerald-600/90 text-white shadow-emerald-600/20' 
                     : 'bg-sky-700/90 text-white shadow-sky-700/20'} 
                   hover:bg-opacity-100 active:scale-[0.98] backdrop-blur-sm`}
          >
            {copied() ? (
              <>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M5 13l4 4L19 7" />
                </svg>
                <span>Скопировано!</span>
              </>
            ) : (
              <>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                <span>Копировать ссылку</span>
              </>
            )}
          </button>

          <p class="text-sm text-gray-600 text-center">
            Отправьте эту ссылку другим игрокам для присоединения к комнате
          </p>
        </div>
      </div>
    </div>
  );
};