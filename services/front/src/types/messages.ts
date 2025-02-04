import type { Player } from "../types/room"
import type { GameMap, GameStat, PlayerData } from "../types/map"

export type PlayersMessage = {
    at: "players";
    players: Player[];
};

export type AuthMessage = {
  at: "auth";
  token: string;
}

export type ReadyMessage = {
  at: "ready";
}

export type ChatMessage = {
  at: "chat";
  user_id: number;
  message: string;
  username: string;
  timestamp: string;
};

export type UpdateMessage = {
  at: 'update';
  map: GameMap;
  turn: number;
  stat: [PlayerData, GameStat];
}