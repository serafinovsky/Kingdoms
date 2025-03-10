import { createResource, For } from "solid-js";
import { useNavigate } from "@solidjs/router";
import api from "../api/axios";
import type { LobbyRoom } from "../types/room";

const fetchRoomsList = async (): Promise<LobbyRoom[]> => {
  try {
    const response = await api.get("/api/v1/rooms/");
    return response.data;
  } catch (error) {
    console.error("Error fetching lobby rooms:", error);
    return [];
  }
};

export const RoomsList = () => {
  const [rooms, { refetch }] = createResource<LobbyRoom[]>(fetchRoomsList);
  const navigate = useNavigate();

  return (
    <div class="p-4 max-w-4xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-4">
          <h2 class="text-2xl font-bold text-gray-800/90">Активные комнаты</h2>
          <button
            onClick={() => refetch()}
            class="p-2 bg-white/60 rounded-xl hover:bg-white/80 
                   active:scale-95 transition-all duration-200
                   shadow-lg shadow-sky-700/10"
            title="Обновить список"
          >
            <svg 
              class="w-5 h-5 text-gray-600/90" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>
        </div>
        <button
          onClick={() => navigate('/maps')}
          class="px-4 py-2 bg-emerald-600/90 text-white rounded-xl text-sm font-medium 
                 shadow-lg shadow-emerald-600/10 hover:bg-opacity-80 
                 active:scale-[0.98] transition-all duration-300 backdrop-blur-sm inline-flex items-center gap-2"
        >
          <svg 
            class="w-5 h-5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
          Создать комнату
        </button>
      </div>

      {rooms.loading ? (
        <div class="flex justify-center items-center p-12">
          <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-sky-500 border-solid" />
        </div>
      ) : !rooms() || rooms()?.length === 0 ? (
        <div class="bg-white/60 backdrop-blur-sm p-8 rounded-2xl shadow-xl 
                    border border-white/10">
          <div class="flex flex-col items-center gap-4">
            <div class="text-gray-500 text-lg">
              Нет активных комнат
            </div>
          </div>
        </div>
      ) : (
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <For each={rooms()}>
            {(room) => (
              <li class="bg-white/60 backdrop-blur-sm p-4 rounded-2xl shadow-xl 
                         border border-white/10 hover:shadow-2xl transition-all duration-300">
                <div class="flex flex-col h-full">
                  <div class="flex-grow space-y-4">
                    <div class="flex justify-between items-start">
                      <h3 class="text-lg font-medium text-gray-800/90">
                        {room.name}
                      </h3>
                      <div class="flex items-center gap-1 px-3 py-1.5 bg-white/70 
                                rounded-xl text-xs font-medium text-gray-700
                                border border-white/20 shadow-sm">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                        </svg>
                        <span>{room.current_players}/{room.max_players}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => navigate(`/rooms/${room.name}`)}
                    class="w-full mt-4 px-4 py-2.5 bg-sky-700/70 text-white rounded-xl 
                           text-sm font-medium shadow-lg shadow-sky-700/10 
                           hover:bg-opacity-80 active:scale-[0.98] 
                           transition-all duration-300 backdrop-blur-sm
                           disabled:opacity-50 disabled:cursor-not-allowed
                           disabled:hover:bg-sky-700/70 disabled:active:scale-100"
                    disabled={room.current_players >= room.max_players}
                  >
                    {room.current_players >= room.max_players 
                      ? 'Комната заполнена' 
                      : 'Присоединиться'}
                  </button>
                </div>
              </li>
            )}
          </For>
        </ul>
      )}
    </div>
  );
};

export default RoomsList;