import { createResource, For } from "solid-js";
import api from "../api/axios";
import { GameMap, MapMeta } from "../types/map";
import { useNavigate } from "@solidjs/router";
import { MapPreview } from "../components/MapPreview";
import { MapInfo } from "../components/MapInfo";

interface MapData {
  id: string;
  map: GameMap;
  meta: MapMeta;
}

const fetchRooms = async (): Promise<MapData[]> => {
  try {
    const response = await api.get("/api/v1/cabinet/maps/");
    return response.data;
  } catch (error) {
    console.error("Error fetching rooms:", error);
    return [];
  }
};

const RoomList = () => {
  const [rooms] = createResource<MapData[]>(fetchRooms);
  const navigate = useNavigate();

  const handleRoomClick = async (id: string) => {
    try {
      const response = await api.post("/api/v1/cabinet/rooms/", { map_id: id });
      navigate(`/rooms/${response.data.room_key}`)
      console.log("Post response:", response.data);
    } catch (error) {
      console.error("Error posting map_id:", error);
    }
  };

  return (
    <div class="p-4 max-w-4xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800/90">Доступные карты</h2>
        <button
          onClick={() => navigate('/maps/')}
          class="px-4 py-2 bg-emerald-600/90 text-white rounded-xl text-sm font-medium 
                 shadow-lg shadow-emerald-600/10 hover:bg-opacity-80 
                 active:scale-[0.98] transition-all duration-300 backdrop-blur-sm"
        >
          Создать карту
        </button>
      </div>
      {rooms.loading ? (
        <div class="flex justify-center items-center p-12">
          <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-sky-500 border-solid"></div>
        </div>
      ) : (
      <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <For each={rooms()}>
          {(room: MapData) => (
            <li class="bg-white/60 backdrop-blur-sm p-4 rounded-2xl shadow-xl 
                      border border-white/10 hover:shadow-2xl transition-all duration-300">
              <div class="flex flex-col h-full">
                <div class="flex-grow space-y-4">
                  <MapPreview data={room.map} />
                  <div class="pt-2 border-t border-gray-100/20">
                    <MapInfo 
                      meta={room.meta} 
                      width={room.map[0]?.length || 0}
                      height={room.map.length || 0}
                    />
                  </div>
                </div>
                <button
                  onClick={() => handleRoomClick(room.id)}
                  class="w-full mt-4 px-4 py-2.5 bg-sky-700/70 text-white rounded-xl text-sm font-medium 
                        shadow-lg shadow-sky-700/10 hover:bg-opacity-80 
                        active:scale-[0.98] transition-all duration-300 backdrop-blur-sm"
                >
                  Начать игру
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

export default RoomList;
