import { For } from 'solid-js';
import { Player } from "../types/room"
import { COLORS } from "../config"

export const PlayersList = (props: {
  players: Player[];
  currentUserId: number;
  onReady?: () => void;
}) => {
  return (
    <div class="mb-8 w-full max-w-2xl mx-auto">
      <h2 class="text-2xl font-bold text-gray-800/90 mb-4">Список игроков</h2>
      <div class="bg-white/60 backdrop-blur-sm p-6 rounded-2xl shadow-xl 
                  border border-white/10 hover:shadow-2xl transition-all duration-300">
        <ul class="space-y-3">
          <For each={props.players}>
            {(player) => {
              const isCurrentUser = player.id === props.currentUserId;
              
              return (
                <li 
                  class={`p-4 rounded-xl flex items-center justify-between
                         transition-all duration-300 backdrop-blur-[2px]
                         ${isCurrentUser && player.status !== 'ready' ? 'cursor-pointer hover:bg-white/50' : ''}
                         ${player.status === 'ready' 
                           ? 'bg-emerald-50/40 border border-emerald-200/10' 
                           : 'bg-gray-50/40 border border-gray-100/10'}`}
                  onClick={() => isCurrentUser && player.status !== 'ready' && props.onReady?.()}
                >
                  <div class="flex items-center gap-3">
                    <div 
                      class="w-4 h-4 rounded-full shadow-lg" 
                      style={{ 
                        "background-color": COLORS[player.color],
                        "box-shadow": `0 2px 8px ${COLORS[player.color]}40`
                      }}
                    />
                    <span class="font-medium text-gray-700/90">{player.username}</span>
                  </div>
                  {player.status === 'ready' ? (
                    <div class="px-2 py-0.5 bg-emerald-600/70 text-white rounded-full 
                              text-xs font-medium shadow-sm shadow-emerald-600/10 backdrop-blur-sm">
                      Готов
                    </div>
                  ) : (
                    <div class="px-2 py-0.5 bg-gray-500/70 text-white rounded-full 
                              text-xs font-medium shadow-sm shadow-gray-500/10 backdrop-blur-sm margin-left-auto">
                      Не готов
                    </div>
                  )}
                </li>
              );
            }}
          </For>
        </ul>
      </div>
    </div>
  );
};