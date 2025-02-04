export type Player = {
    id: number;
    username: string;
    color: number;
    status: 'ready' | 'win' | 'lose';
};


// interface PlayerData {
//   id: number;
//   username: string;
//   color: number;
//   status: 'ready' | 'win' | 'lose';
// }

// interface GameStat {
//   fields: number;
//   power: number;
// }

// interface UpdateMessage {
//   at: 'update';
//   map: GameMap;
//   turn: number;
//   stat: [PlayerData, GameStat];
// }

export type Cursor = {
    row: number;
    col: number;
};

export type CursorMove = {
    previous: Cursor;
    current: Cursor;
};