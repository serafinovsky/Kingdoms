import { For, Index, createSignal, onCleanup, createMemo, createEffect, batch, Component } from 'solid-js';
import { KingIcon } from "./KingIcon";
import { FieldIcon } from "./FieldIcon";
import { CastleIcon } from "./CastleIcon";
import { COLORS } from '../config';
import type { Cell } from "../types/map";
import type { Player, Cursor, CursorMove } from "../types/room"




const GameCell: Component<{
  cell: Cell;
  rowIndex: number;
  colIndex: number;
  isSelected: boolean;
  isPlayerCell: boolean;
  color: string;
  onClick: () => void;
}> = (props) => {
  const cellClass = createMemo(() => `rounded-sm bg-white/90 
    ${props.isSelected ? 'ring-2 ring-sky-500 shadow-lg' : ''} 
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
    <td onClick={props.onClick} class={cellClass()}>
      {CellIcon()}
    </td>
  );
};

const ColumnHeader: Component<{
  index: number;
  getLabel: (index: number) => string;
  coordinateClass: string;
}> = (props) => (
  <th class={props.coordinateClass}>
    {props.getLabel(props.index)}
  </th>
);

const RowHeader: Component<{
  index: number;
  coordinateClass: string;
}> = (props) => (
  <td class={props.coordinateClass}>
    {props.index + 1}
  </td>
);

type GameBoardProps = {
  data: Cell[][];
  players: Player[];
  currentUserId: number;
  initialCursor: Cursor;
  onCellClick: (rowIndex: number, colIndex: number, cell: Cell) => void;
  onCursorMove: (move: CursorMove) => void;
};

export const GameBoard: Component<GameBoardProps> = (props) => {
  const [cursor, setCursor] = createSignal<Cursor>(props.initialCursor);

  const playerColors = createMemo(() => 
    new Map(props.players.map(p => [p.id, COLORS[p.color]]))
  );

  const getColor = createMemo(() => (cell: Cell) => {
    if (cell.player !== undefined) {
      return playerColors().get(cell.player) ?? '#d4d4d8';
    }
    return cell.type === 'hide' ? '#f4f4f5' : 
           cell.type === 'block' ? '#71717a' : '#d4d4d8';
  });

  const isPlayerCell = createMemo(() => (cell: Cell) => 
    (cell.type === 'field' || cell.type === 'king') && 
    cell.player === props.currentUserId
  );

  const isCursorAt = createMemo(() => (row: number, col: number) => {
    const current = cursor();
    return current?.row === row && current?.col === col;
  });

  const moveCursor = (newCursor: Cursor) => {
    batch(() => {
      const previousCursor = { ...cursor() };
      setCursor(newCursor);
      props.onCursorMove?.({ previous: previousCursor, current: newCursor });
    });
  };

  const createCellClickHandler = (rowIndex: number, colIndex: number, cell: Cell) => 
    createMemo(() => () => {
      const newCursor = { row: rowIndex, col: colIndex };
      batch(() => {
        setCursor(newCursor);
        props.onCellClick(rowIndex, colIndex, cell);
      });
    });

  const handleKeyDown = createMemo(() => (e: KeyboardEvent) => {
    const current = cursor()!;

    let newCursor = { ...current };
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
      default:
        return;
    }

    if (newCursor.row !== current.row || newCursor.col !== current.col) {
      e.preventDefault();
      moveCursor(newCursor);
    }
  });

  createEffect(() => {
    const handler = handleKeyDown();
    window.addEventListener('keydown', handler);
    onCleanup(() => window.removeEventListener('keydown', handler));
  });

  const getColumnLabel = (index: number) => String.fromCharCode(65 + index);

  const getCoordinateClass = createMemo(() => (index: number, type: 'row' | 'col') => {
    const current = cursor();
    const isHighlighted = current && (
      type === 'row' ? current.row === index : current.col === index
    );
    
    return `w-6 h-6 text-sm font-medium ${
      isHighlighted ? 'text-sky-600/90 scale-110' : 'text-gray-500/80'
    }`;
  });

  const tableClass = createMemo(() => 
    `border-separate border-spacing-1 bg-white/60 backdrop-blur-sm p-4 
    rounded-2xl shadow-xl border border-white/10`
  );

  return (
    <div class="p-4 w-full" tabIndex={0}>
      <div class="flex justify-center">
        <table class={tableClass()}>
          <thead>
            <tr>
              <th class="w-6 h-6" />
              <Index each={props.data[0]}>
                {(_, colIndex) => (
                  <ColumnHeader
                    index={colIndex}
                    getLabel={getColumnLabel}
                    coordinateClass={getCoordinateClass()(colIndex, 'col')}
                  />
                )}
              </Index>
            </tr>
          </thead>
          <tbody>
            <Index each={props.data}>
              {(row, rowIndex) => (
                <tr>
                  <RowHeader
                    index={rowIndex}
                    coordinateClass={getCoordinateClass()(rowIndex, 'row')}
                  />
                  <Index each={row()}>
                    {(cell, colIndex) => (
                      <GameCell
                        cell={cell()}
                        rowIndex={rowIndex}
                        colIndex={colIndex}
                        isSelected={isCursorAt()(rowIndex, colIndex)}
                        isPlayerCell={isPlayerCell()(cell())}
                        color={getColor()(cell())}
                        onClick={createCellClickHandler(rowIndex, colIndex, cell())()}
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
