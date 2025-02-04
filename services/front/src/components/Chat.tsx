import { createSignal, For, Show } from 'solid-js';

type ChatMessage = {
  id: number;
  userId: number;
  username: string;
  text: string;
  timestamp: string;
};

type ChatProps = {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
};

const sanitizeText = (text: string) => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.textContent || '';
};

export const Chat = (props: ChatProps) => {
  const [message, setMessage] = createSignal('');
  const [isCollapsed, setIsCollapsed] = createSignal(false);

  const handleSubmit = (e: Event) => {
    e.preventDefault();
    const text = message().trim();
    if (text) {
      props.onSendMessage(sanitizeText(text));
      setMessage('');
    }
  };

  return (
    <div class={`fixed bottom-4 right-4 w-80 bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl 
                border border-white/20 overflow-hidden transition-all duration-300
                hover:shadow-2xl ${isCollapsed() ? 'h-[52px]' : 'h-[500px]'}`}>
      {/* Chat Header */}
      <div class="px-4 py-3 border-b border-gray-100/20 bg-white/60 backdrop-blur-md cursor-pointer"
           onClick={() => setIsCollapsed(prev => !prev)}>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse 
                        shadow-lg shadow-emerald-500/20"></div>
            <h3 class="font-medium text-gray-700/90">Чат комнаты</h3>
          </div>
          <svg 
            class={`w-4 h-4 text-gray-500/80 transition-transform duration-300
                   ${isCollapsed() ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <Show when={!isCollapsed()}>
        <div class="flex flex-col h-[calc(500px-52px)]">
          {/* Messages List */}
          <div class="flex-1 p-4 space-y-2 overflow-y-auto scrollbar-thin 
                      scrollbar-thumb-gray-200/80 scrollbar-track-transparent">
            <Show
              when={props.messages.length > 0}
              fallback={
                <div class="flex flex-col items-center justify-center h-20 text-gray-400 space-y-2
                            backdrop-blur-sm bg-white/30 rounded-xl border border-white/20">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span class="text-sm">Нет сообщений</span>
                </div>
              }
            >
              <For each={props.messages}>
                {(message) => (
                  <div class="group flex flex-col p-2 rounded-xl transition-all duration-200
                              hover:bg-white/60 backdrop-blur-[2px] border border-transparent 
                              hover:border-white/20 hover:shadow-sm">
                    <div class="flex items-baseline justify-between">
                      <span class="font-medium text-sm text-gray-700/90">
                        {sanitizeText(message.username)}
                      </span>
                      <span class="text-xs text-gray-400 opacity-0 group-hover:opacity-100 
                                 transition-opacity duration-200">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p class="text-sm text-gray-600/90 break-words mt-1">
                      {sanitizeText(message.text)}
                    </p>
                  </div>
                )}
              </For>
            </Show>
          </div>

          {/* Message Input */}
          <form onSubmit={handleSubmit} 
                class="p-3 bg-white/60 backdrop-blur-md border-t border-gray-100/20">
            <div class="flex gap-2">
              <input
                type="text"
                value={message()}
                onInput={(e) => setMessage(e.currentTarget.value)}
                placeholder="Введите сообщение..."
                class="flex-1 px-4 py-2 text-sm bg-white/70 rounded-xl border-none
                       focus:outline-none focus:ring-2 focus:ring-sky-500/30 
                       focus:bg-white/90 placeholder:text-gray-400/80 transition-all 
                       backdrop-blur-sm shadow-inner shadow-white/10"
              />
              <button
                type="submit"
                disabled={!message().trim()}
                class="p-2 aspect-square bg-sky-700/70 text-white rounded-xl
                       hover:bg-opacity-80 active:scale-[0.98] transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100
                       backdrop-blur-sm flex items-center justify-center 
                       shadow-lg shadow-sky-700/10"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      </Show>
    </div>
  );
};