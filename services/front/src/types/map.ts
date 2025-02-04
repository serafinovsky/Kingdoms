export enum CellType {
  SPAWN = "spawn",
  HIDE = "hide",
  KING = "king",
  BLOCKER = "block",
  FIELD = "field",
  CASTLE = "castle",
}

export type Cell = {
  type: CellType;
  power?: number;
  player?: number;
};

export type GameMap = Cell[][];

export type Point = [number, number];

export interface MapMeta {
  points_of_interest: { [key in CellType]: Point[] };
}

export type PlayerData = {
  id: number;
  username: string;
  color: number;
  status: 'ready' | 'win' | 'lose';
}

export type GameStat = {
  fields: number;
  power: number;
}
