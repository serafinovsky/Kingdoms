import { createSignal } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { SpawnIcon } from "./SpawnIcon";
import { FieldIcon } from "./FieldIcon";
import { CastleIcon } from "./CastleIcon";
import { MapPreview } from "./MapPreview";
import { CellType } from "../types/map";
import type { Cell } from "../types/map";
import api from "../api/axios";


export const MapEditor = (props: {}) => {
  const navigate = useNavigate();
  const [width, setWidth] = createSignal(10);
  const [height, setHeight] = createSignal(10);
  const [selectedType, setSelectedType] = createSignal<CellType>(CellType.FIELD);
  const [error, setError] = createSignal<string | null>(null);
  const [isLoading, setIsLoading] = createSignal(false);
  const [map, setMap] = createSignal<Cell[][]>(
    Array(height()).fill(0).map(() => 
      Array(width()).fill(0).map(() => ({ 
        type: CellType.FIELD 
      }))
    )
  );

  const getColor = (cell: Cell) => {
    switch (cell.type) {
      case CellType.BLOCKER:
        return '#71717a';
      case CellType.CASTLE:
        return '#0369A1';
      case CellType.SPAWN:
        return '#0369A1';
      default:
        return '#d4d4d8';
    }
  };

  const handleWidthChange = (newWidth: number) => {
    if (newWidth >= 5 && newWidth <= 20) {
      setWidth(newWidth);
      setMap(prevMap => prevMap.map(row => {
        if (newWidth > row.length) {
          return [...row, ...Array(newWidth - row.length).fill(0).map(() => ({ 
            type: CellType.FIELD 
          }))];
        }
        return row.slice(0, newWidth);
      }));
    }
  };

  const handleHeightChange = (newHeight: number) => {
    if (newHeight >= 5 && newHeight <= 20) {
      setHeight(newHeight);
      setMap(prevMap => {
        if (newHeight > prevMap.length) {
          return [
            ...prevMap,
            ...Array(newHeight - prevMap.length).fill(0).map(() => 
              Array(width()).fill(0).map(() => ({ 
                type: CellType.FIELD 
              }))
            )
          ];
        }
        return prevMap.slice(0, newHeight);
      });
    }
  };

  const handleCellClick = (rowIndex: number, colIndex: number) => {
    if (isLoading()) return;
    
    setMap(prevMap => prevMap.map((row, i) =>
      row.map((cell, j) =>
        i === rowIndex && j === colIndex
          ? { ...cell, type: selectedType() }
          : cell
      )
    ));
    setError(null);
  };

  const handleMapClick = (e: MouseEvent) => {
    if (isLoading()) return;

    const td = (e.target as HTMLElement).closest('td');
    if (td) {
      const row = td.parentElement as HTMLTableRowElement;
      const tbody = row?.parentElement as HTMLTableSectionElement;
      if (row && tbody) {
        const colIndex = Array.from(row.cells).indexOf(td as HTMLTableCellElement);
        const rowIndex = Array.from(tbody.rows).indexOf(row);
        if (rowIndex !== -1 && colIndex !== -1) {
          handleCellClick(rowIndex, colIndex);
        }
      }
    }
  };

  const validateMap = (mapData: Cell[][]): boolean => {
    const spawnCount = mapData.flat().filter(cell => cell.type === CellType.SPAWN).length;
    if (spawnCount < 2) {
      setError('Необходимо разместить минимум 2 точки появления');
      return false;
    }
    return true;
  };

  const handleSave = async () => {
    if (isLoading()) return;

    try {
      const currentMap = map();
      
      if (!validateMap(currentMap)) {
        return;
      }

      setIsLoading(true);
      const response = await api.post("/api/v1/cabinet/maps/", {
        map: currentMap,
      });

      if (response.status === 201) {
        setError(null);
        navigate('/');
      }
    } catch (err) {
      console.error('Failed to save map:', err);
      setError('Произошла ошибка при сохранении карты');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div class="w-full max-w-4xl mx-auto p-6">
      <div class="relative bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-xl 
                  border border-white/20 hover:shadow-2xl transition-all duration-300">
        {isLoading() && (
          <div class="absolute inset-0 flex items-center justify-center 
                      bg-white/80 backdrop-blur-sm rounded-2xl z-50">
            <div class="flex flex-col items-center gap-2">
              <div class="w-8 h-8 border-4 border-sky-600/50 border-t-sky-600 
                          rounded-full animate-spin" />
              <div class="text-sm text-gray-600">Сохранение карты...</div>
            </div>
          </div>
        )}

        <div class="flex gap-4 mb-6">
          <div class="flex-1 space-y-2">
            <label class="block text-sm font-medium text-gray-700">Ширина</label>
            <div class="relative flex items-center">
              <button
                onClick={() => handleWidthChange(width() - 1)}
                disabled={width() <= 5 || isLoading()}
                class="absolute left-0 w-10 h-full flex items-center justify-center text-gray-500 
                       hover:text-sky-600 disabled:opacity-50 disabled:hover:text-gray-500 
                       transition-colors"
              >
                <span class="text-xl">−</span>
              </button>
              <input
                type="text"
                min="5"
                max="20"
                value={width()}
                disabled={isLoading()}
                onInput={(e) => handleWidthChange(parseInt(e.currentTarget.value))}
                class="w-full px-12 py-2 text-center rounded-lg border border-gray-200 
                       focus:ring-2 focus:ring-sky-500 focus:border-transparent
                       disabled:opacity-50 disabled:bg-gray-50"
              />
              <button
                onClick={() => handleWidthChange(width() + 1)}
                disabled={width() >= 20 || isLoading()}
                class="absolute right-0 w-10 h-full flex items-center justify-center text-gray-500 
                       hover:text-sky-600 disabled:opacity-50 disabled:hover:text-gray-500 
                       transition-colors"
              >
                <span class="text-xl">+</span>
              </button>
            </div>
          </div>
          <div class="flex-1 space-y-2">
            <label class="block text-sm font-medium text-gray-700">Высота</label>
            <div class="relative flex items-center">
              <button
                onClick={() => handleHeightChange(height() - 1)}
                disabled={height() <= 5 || isLoading()}
                class="absolute left-0 w-10 h-full flex items-center justify-center text-gray-500 
                       hover:text-sky-600 disabled:opacity-50 disabled:hover:text-gray-500 
                       transition-colors"
              >
                <span class="text-xl">−</span>
              </button>
              <input
                type="text"
                min="5"
                max="20"
                value={height()}
                disabled={isLoading()}
                onInput={(e) => handleHeightChange(parseInt(e.currentTarget.value))}
                class="w-full px-12 py-2 text-center rounded-lg border border-gray-200 
                       focus:ring-2 focus:ring-sky-500 focus:border-transparent
                       disabled:opacity-50 disabled:bg-gray-50"
              />
              <button
                onClick={() => handleHeightChange(height() + 1)}
                disabled={height() >= 20 || isLoading()}
                class="absolute right-0 w-10 h-full flex items-center justify-center text-gray-500 
                       hover:text-sky-600 disabled:opacity-50 disabled:hover:text-gray-500 
                       transition-colors"
              >
                <span class="text-xl">+</span>
              </button>
            </div>
          </div>
        </div>

        <div class="flex gap-2 mb-6">
          <div class="flex gap-2">
            <div
              onClick={() => setSelectedType(CellType.FIELD)}
              class={`p-2 rounded-lg cursor-pointer 
                ${selectedType() === CellType.FIELD ? 'ring-2 ring-sky-700' : ''}`
              }
            >
              <FieldIcon color={getColor({type: CellType.FIELD})} class="w-6 h-6" />
            </div>
            <div
              onClick={() => setSelectedType(CellType.CASTLE)}
              class={`p-2 rounded-lg cursor-pointer 
                ${selectedType() === CellType.CASTLE ? 'ring-2 ring-sky-700' : ''}`
              }
            >
              <CastleIcon color={getColor({type: CellType.CASTLE})} class="w-6 h-6" />
            </div>
            <div
              onClick={() => setSelectedType(CellType.BLOCKER)}
              class={`p-2 rounded-lg cursor-pointer 
                ${selectedType() === CellType.BLOCKER ? 'ring-2 ring-sky-700' : ''}`
              }
            >
              <FieldIcon color={getColor({type: CellType.BLOCKER})} class="w-6 h-6" />
            </div>
            <div
              onClick={() => setSelectedType(CellType.SPAWN)}
              class={`p-2 rounded-lg cursor-pointer hover:bg-gray-100 
                ${selectedType() === CellType.SPAWN ? 'ring-2 ring-sky-700' : ''}`
              }
            >
              <SpawnIcon color={getColor({type: CellType.SPAWN})} class="w-6 h-6" />
            </div>
          </div>
        </div>

        <div class="flex justify-center">
          <div class="overflow-auto p-4" onClick={handleMapClick}>
            <MapPreview data={map()} size='large'/>
          </div>
        </div>

        <div class="mt-6">
          {error() && (
            <div class="text-red-500 text-sm mb-2">
              {error()}
            </div>
          )}
          <div class="flex justify-end">
            <button
              onClick={handleSave}
              disabled={isLoading()}
              class="px-6 py-2 bg-emerald-600/90 text-white rounded-lg
                     hover:bg-emerald-600 active:scale-95 transition-all duration-150
                     disabled:opacity-50 disabled:hover:bg-emerald-600/90 
                     disabled:cursor-not-allowed disabled:active:scale-100"
            >
              {isLoading() ? 'Сохранение...' : 'Сохранить карту'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};