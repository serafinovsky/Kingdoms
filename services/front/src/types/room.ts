export type Player = {
    id: number;
    username: string;
    color: number;
    status: 'ready' | 'win' | 'lose';
};

export type LobbyRoom = {
    name: string;
    max_players: number;
    current_players: number;
};


export type Cursor = {
    row: number;
    col: number;
};

export type CursorMove = {
    previous?: Cursor;
    current?: Cursor;
};