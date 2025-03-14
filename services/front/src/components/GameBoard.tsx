import { For, Index, createSignal, onCleanup, createMemo, createEffect, batch, Component } from 'solid-js';
import { KingIcon } from "./KingIcon";
import { FieldIcon } from "./FieldIcon";
import { CastleIcon } from "./CastleIcon";
import { COLORS } from '../config';
import type { Cell } from "../types/map";
import { CellType } from "../types/map";
import type { Player, Cursor, CursorMove } from "../types/room"


type Direction = 'up' | 'down' | 'left' | 'right';
type CellCoord = `${number},${number}`;

const DirectionArrow: Component<{ direction: Direction }> = (props) => {
  const position = createMemo(() => {
    switch (props.direction) {
      case 'up': return 'top-0.5';
      case 'down': return 'bottom-0.5';
      case 'left': return 'left-0.5';
      case 'right': return 'right-0.5';
      default: return '';
    }
  });

  const rotation = createMemo(() => {
    switch (props.direction) {
      case 'up': return '-rotate-90';
      case 'down': return 'rotate-90';
      case 'left': return 'rotate-180';
      default: return '';
    }
  });

  return (
    <div class={`absolute ${position()} ${rotation()} w-4 h-4 z-10`}>
      <svg
        class="absolute inset-0 text-white/90 mix-blend-difference"
        fill="none"
        stroke="currentColor"
        stroke-width="4"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M14 5l7 7m0 0l-7 7m7-7H3"
        />
      </svg>
      <svg
        class="absolute inset-0 text-grey-950"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M14 5l7 7m0 0l-7 7m7-7H3"
        />
      </svg>
    </div>
  );
};

const GameCell: Component<{
  cell: Cell;
  rowIndex: number;
  colIndex: number;
  isSelected: boolean;
  isPlayerCell: boolean;
  color: string;
  directions: Direction[];
  onClick: () => void;
}> = (props) => {
  const cellClass = createMemo(() => `rounded-sm bg-white/90 relative
    ${props.isSelected ? 'ring-2 ring-stone-950 shadow-lg' : ''} 
    ${props.isPlayerCell ? 'hover:ring-2 hover:ring-emerald-500 hover:shadow-lg' : ''}
    w-8 h-8
    ${props.isPlayerCell ? 'cursor-pointer' : 'cursor-default'}`
  );

  const CellIcon = createMemo(() => {
    switch (props.cell.type) {
      case "king": return <KingIcon color={props.color} number={props.cell.power} />;
      case "castle": return <CastleIcon color={props.color} number={props.cell.power} />;
      default: return <FieldIcon color={props.color} number={props.cell.power} />;
    }
  });

  return (
    <td 
      onClick={() => props.isPlayerCell && props.onClick()} 
      class={cellClass()}
    >
      {CellIcon()}
      <div class="absolute inset-0 flex items-center justify-center">
        <For each={props.directions}>
          {(direction) => <DirectionArrow direction={direction} />}
        </For>
      </div>
    </td>
  );
};


type GameBoardProps = {
  data: Cell[][];
  players: Player[];
  currentUserId: number;
  gameCursor: Cursor | undefined;
  previousCursor: Cursor | undefined;
  onCellClick: (rowIndex: number, colIndex: number, cell: Cell) => void;
  onCursorMove: (move: CursorMove) => void;
};

export const GameBoard: Component<GameBoardProps> = (props) => {
  const findKingPosition = (): Cursor => {
    for (let row = 0; row < props.data.length; row++) {
      for (let col = 0; col < props.data[row].length; col++) {
        const cell = props.data[row][col];
        if (cell.type === CellType.KING && cell.player === props.currentUserId) {
          return { row, col };
        }
      }
    }
    return { row: 0, col: 0 };
  };

  const [cursor, setCursor] = createSignal<Cursor>(findKingPosition());
  const [directions, setDirections] = createSignal<Map<CellCoord, Direction[]>>(new Map());
  const [resetDirections, setResetDirections] = createSignal(false);

  const getDirection = (from: Cursor, to: Cursor): Direction | null => {
    if (from.row > to.row) return 'up';
    if (from.row < to.row) return 'down';
    if (from.col > to.col) return 'left';
    if (from.col < to.col) return 'right';
    return null;
  };

  const getCellDirections = (rowIndex: number, colIndex: number) => {
    const key: CellCoord = `${rowIndex},${colIndex}`;
    return directions().get(key) || [];
  };

  const addDirection = (coord: CellCoord, direction: Direction) => {
    setDirections(prev => {
      const next = new Map(prev);
      const current = next.get(coord) || [];
      next.set(coord, [...current, direction]);
      return next;
    });
  };
  const playerColors = createMemo(() => 
    new Map(props.players.map(p => [p.id, COLORS[p.color]]))
  );

  const getColor = createMemo(() => (cell: Cell) => {
    if (cell.player !== undefined) {
      return playerColors().get(cell.player) ?? '#d4d4d8';
    }
    return cell.type === undefined ? '#f4f4f5' : 
           cell.type === 'block' ? '#71717a' : '#d4d4d8';
  });

  const isPlayerCell = createMemo(() => (cell: Cell) => 
    cell.player === props.currentUserId
  );

  const isCursorAt = createMemo(() => (row: number, col: number) => {
    const current = cursor();
    return current?.row === row && current?.col === col;
  });

  const allowedMove = (cursor: Cursor): boolean => {
    const cell = props.data[cursor.row][cursor.col];
    const hasValidPower = cell.power !== undefined && cell.power > 1;
    return (cell.player === props.currentUserId && hasValidPower) || directions().size !== 0;
  };

  const moveCursor = (newCursor: Cursor, resetCursor: boolean) => {
    batch(() => {
      if (resetCursor) {
        setResetDirections(true);
        props.onCursorMove?.({});
        return;
      }

      setResetDirections(false);
      const previousCursor = { ...cursor() };
      if (previousCursor.row !== newCursor.row || previousCursor.col !== newCursor.col) {
        const direction = getDirection(previousCursor, newCursor);
        if (direction && allowedMove(previousCursor)) {
          const coord: CellCoord = `${previousCursor.row},${previousCursor.col}`;
          addDirection(coord, direction);
        }

        setCursor(newCursor);
        props.onCursorMove?.({ previous: previousCursor, current: newCursor });
      }
    });
  };

  const createCellClickHandler = (rowIndex: number, colIndex: number, cell: Cell) => () => {
    if (cell.player === props.currentUserId) {
      const newCursor = { row: rowIndex, col: colIndex };
      batch(() => {
        setCursor(newCursor);
        props.onCellClick(rowIndex, colIndex, cell);
      });
    }
  };

  const handleKeyDown = createMemo(() => (e: KeyboardEvent) => {
    const current = cursor()!;

    let newCursor = { ...current };
    let resetCursor = false
    switch (e.key) {
      case 'ArrowUp':
        if (current.row > 0) newCursor.row--;
        break;
      case 'ArrowDown':
        if (current.row < props.data.length - 1) newCursor.row++;
        break;
      case 'ArrowLeft':
        if (current.col > 0) newCursor.col--;
        break;
      case 'ArrowRight':
        if (current.col < props.data[0].length - 1) newCursor.col++;
        break;
      case 'Escape':
        resetCursor = true;
        break
      default:
        return;
    }

    if (newCursor.row !== current.row || newCursor.col !== current.col || resetCursor) {
      e.preventDefault();
      moveCursor(newCursor, resetCursor);
    }
  });

  createEffect(() => {
    const handler = handleKeyDown();
    window.addEventListener('keydown', handler);
    onCleanup(() => window.removeEventListener('keydown', handler));
  });

  createEffect(() => {
    if (props.gameCursor === undefined) {
      setResetDirections(true);
    } else {
      setResetDirections(false);
    }
  });

  createEffect(() => {
    if (resetDirections() && directions().size > 0) {
      setDirections(new Map());
      return;
    }
  })

  createEffect(() => {
    if (props.previousCursor) {
      const coord: CellCoord = `${props.previousCursor.row},${props.previousCursor.col}`;
      setDirections(prev => {
        const next = new Map(prev);
        const directions = next.get(coord);
        if (directions?.length) {
          const remaining = directions.slice(1);
          if (remaining.length > 0) {
            next.set(coord, remaining);
          } else {
            next.delete(coord);
          }
        }
        
        return next;
      });
    }
  });

  const tableClass = createMemo(() => 
    `border-separate border-spacing-1 bg-white/60 backdrop-blur-sm p-4 
    rounded-2xl shadow-xl border border-white/10`
  );

  const getUniqueCellDirections = (rowIndex: number, colIndex: number): Direction[] => {
    const key: CellCoord = `${rowIndex},${colIndex}`;
    const allDirections = directions().get(key) || [];
    return [...new Set(allDirections)];
  };

  return (
    <div class="p-4 w-full" tabIndex={0}>
      <div class="flex justify-center">
        <table class={tableClass()}>
          <tbody>
            <Index each={props.data}>
              {(row, rowIndex) => (
                <tr>
                  <Index each={row()}>
                    {(cell, colIndex) => (
                      <GameCell
                        cell={cell()}
                        rowIndex={rowIndex}
                        colIndex={colIndex}
                        isSelected={isCursorAt()(rowIndex, colIndex)}
                        isPlayerCell={isPlayerCell()(cell())}
                        color={getColor()(cell())}
                        directions={getUniqueCellDirections(rowIndex, colIndex)}
                        onClick={createCellClickHandler(rowIndex, colIndex, cell())}
                      />
                    )}
                  </Index>
                </tr>
              )}
            </Index>
          </tbody>
        </table>
      </div>
    </div>
  );
};