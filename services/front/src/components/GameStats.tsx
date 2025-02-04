import { Component, For } from 'solid-js';
import type { PlayerData, GameStat } from '../types/map';
import { COLORS } from '../config';

type GameStatsProps = {
  turn: number;
  stats: [PlayerData, GameStat][];
};

export const GameStats: Component<GameStatsProps> = (props) => {
  return (
    <div class="bg-white/60 backdrop-blur-sm p-4 rounded-2xl shadow-xl border border-white/10 
                hover:shadow-2xl transition-all duration-300 w-96">
      <div class="text-center mb-4">
        <span class="text-gray-500">Ход</span>
        <span class="text-2xl font-bold text-sky-600 ml-2">{props.turn}</span>
      </div>
      
      <div class="space-y-2">
        <For each={props.stats}>
          {([player, stat]) => (
            <div class="flex items-center justify-between p-2 rounded-xl bg-white/90">
              <div class="flex items-center gap-2">
                <div 
                  class="w-3 h-3 rounded-full" 
                  style={{ background: `${COLORS[player.color]}` }}
                />
                <span class="text-sm font-medium text-gray-700">
                  {player.username}
                </span>
              </div>
              <div class="flex gap-4">
                <div class="text-xs text-gray-500">
                  Поля: <span class="font-semibold text-gray-700">{stat.fields}</span>
                </div>
                <div class="text-xs text-gray-500">
                  Сила: <span class="font-semibold text-gray-700">{stat.power}</span>
                </div>
              </div>
            </div>
          )}
        </For>
      </div>
    </div>
  );
};