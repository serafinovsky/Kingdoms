import { CellType } from "../types/map";
import { CastleIcon } from "./CastleIcon";
import { FieldIcon } from "./FieldIcon";
import type { MapMeta } from "../types/map";

interface MapInfoProps {
  meta: MapMeta;
  width: number;
  height: number;
}

export function MapInfo(props: MapInfoProps) {
  const getCellTypeIcon = (type: CellType, color: string = "#71717a") => {
    switch (type) {
      case CellType.CASTLE:
        return <CastleIcon color={color} class="w-4 h-4" />;
      default:
        return <FieldIcon color={color} class="w-4 h-4" />;
    }
  };

  const playerCount = props.meta.points_of_interest[CellType.SPAWN]?.length || 0;

  return (
    <div class="flex flex-wrap items-center gap-2">
      <div class="inline-flex items-center px-2 py-1 text-sm text-gray-600 
                  bg-gray-50/50 rounded-lg backdrop-blur-sm">
        <svg class="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none">
          <path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" 
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span>
          {playerCount} {playerCount === 1 ? 'игрок' : playerCount < 5 ? 'игрока' : 'игроков'}
        </span>
      </div>

      <div class="inline-flex items-center px-2 py-1 text-sm text-gray-600 
                  bg-gray-50/50 rounded-lg backdrop-blur-sm">
        <span class="mr-1.5">{getCellTypeIcon(CellType.FIELD)}</span>
        <span>{props.width}×{props.height}</span>
      </div>

      {Object.entries(props.meta.points_of_interest).map(([type, points]) => (
        type !== CellType.SPAWN && points.length > 0 && (
          <div class="inline-flex items-center px-2 py-1 text-sm text-gray-600 
                      bg-gray-50/50 rounded-lg backdrop-blur-sm">
            <span class="mr-1.5">{getCellTypeIcon(type as CellType)}</span>
            <span>{points.length}</span>
          </div>
        )
      ))}
    </div>
  );
}