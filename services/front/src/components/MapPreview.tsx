import { For } from 'solid-js';
import { FieldIcon } from "./FieldIcon";
import { CastleIcon } from "./CastleIcon";
import { SpawnIcon } from "./SpawnIcon";
import type { Cell } from "../types/map";

type MapPreviewProps = {
  data: Cell[][];
  size?: 'small' | 'medium' | 'large';
};

export const MapPreview = (props: MapPreviewProps) => {
  const getSizeClass = () => {
    if (!props.size || props.size === 'small') {
      return 'w-3 h-3';
    } else if (props.size === 'medium') {
      return 'w-5 h-5';
    } else {
      return 'w-7 h-7';
    }
  };

  const getColor = (cell: Cell) => {
    switch (cell.type) {
      case 'block':
        return '#71717a';
      case 'castle':
        return '#0369A1';
      case 'spawn':
        return '#0369A1';
      default:
        return '#d4d4d8';
    }
  };

  return (
    <div class="w-full">
      <div class="flex justify-center">
        <table class="border-separate border-spacing-[1px] bg-white/90 p-2 rounded-lg shadow-sm">
          <tbody>
            <For each={props.data}>
              {(row) => (
                <tr>
                  <For each={row}>
                    {(cell) => (
                      <td class="rounded-md bg-white transition-colors">
                        {cell.type === "spawn" ? (
                          <SpawnIcon color={getColor(cell)} class={getSizeClass()} />
                        ) : cell.type === "castle" ? (
                          <CastleIcon color={getColor(cell)} class={getSizeClass()} />
                        ) : cell.type === "block" ? (
                          <FieldIcon color={getColor(cell)} class={getSizeClass()} />
                        ) : (
                          <FieldIcon color={getColor(cell)} class={getSizeClass()} />
                        )}
                      </td>
                    )}
                  </For>
                </tr>
              )}
            </For>
          </tbody>
        </table>
      </div>
    </div>
  );
};