import { useParams } from "@solidjs/router";
import { createSignal, createEffect, onCleanup, batch } from "solid-js";
import { authActions } from "../stores/authStore";
import { userStore } from "../stores/userStore";
import { Chat } from "../components/Chat";
import { ColorSelector } from "../components/ColorSelector";
import { ShareLink } from "../components/ShareLink";
import { PlayersList } from "../components/PlayersList";
import { ErrorMessage } from "../components/ErrorMessage";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { GameBoard } from "../components/GameBoard";
import { GameStats } from "../components/GameStats";
import { TutorialPopup } from "../components/TutorialPopup";
import type { Player, CursorMove, Cursor } from "../types/room";
import type { PlayerData, GameStat } from "../types/map";
import type { Cell, GameMap } from "../types/map";
import {
  PlayersMessage,
  AuthMessage,
  ChatMessage,
  ReadyMessage,
  UpdateMessage,
} from "../types/messages";
import { BASE_WS_URL } from "../config";

type Status = "connecting" | "config" | "active" | "error";

const getWebSocketErrorMessage = (code: number): string => {
  switch (code) {
    case 4010:
      return "Комната заполнена";
    case 4020:
      return "Игра уже началась";
    case 4030:
      return "Ошибка авторизации";
    case 4031:
      return "Ошибка авторизации";
    case 4040:
      return "Комната не найдена";
    case 5000:
      return "Внутренняя ошибка сервера";
    default:
      return "Неизвестная ошибка";
  }
};

type ChatLine = {
  id: number;
  userId: number;
  username: string;
  text: string;
  timestamp: string;
};

function makeMessage(text: string): ChatMessage {
  return {
    at: "chat",
    user_id: userStore.user.user_id,
    message: text,
    username: userStore.user.username,
    timestamp: new Date().toISOString(),
  };
}

export default function Room() {
  const params = useParams();
  const [status, setStatus] = createSignal<Status>("connecting");
  const [players, setPlayers] = createSignal<Player[]>([]);
  const [data, setData] = createSignal<GameMap | undefined>(undefined);
  const [socket, setSocket] = createSignal<WebSocket | null>(null);
  const [messages, setMessages] = createSignal<ChatLine[]>([]);
  const [selectedColors, setSelectedColors] = createSignal<number[]>([]);
  const [turn, setTurn] = createSignal(0);
  const [stats, setStats] = createSignal<[PlayerData, GameStat][]>([]);
  const [currentCursor, setCurrentCursor] = createSignal<Cursor | undefined>();
  const [previousCursor, setPreviousCursor] = createSignal<Cursor | undefined>();
  const [errorMessage, setErrorMessage] = createSignal("Что-то пошло не так");
  const [showTutorial, setShowTutorial] = createSignal(!localStorage.getItem('kingdomsTutorialSeen'));

  let reconnectAttempts = 0;
  const MAX_RECONNECT_ATTEMPTS = 10;
  const RECONNECT_DELAY = 0;

  const handleColorSelect = (colorIndex: number) => {
    socket()?.send(
      JSON.stringify({
        at: "color",
        color: colorIndex,
      })
    );
  };

  const connectWebSocket = () => {
    if (userStore.user.username === "") return;

    const getParams = new URLSearchParams({
      user_id: userStore.user.user_id.toString(),
      username: userStore.user.username,
    });
    const ws = new WebSocket(
      `${BASE_WS_URL}/ws/rooms/${params.roomId}/?${getParams.toString()}`
    );

    ws.onopen = () => {
      console.log("WebSocket connected");
      reconnectAttempts = 0;
      const authMessage: AuthMessage = {
        at: "auth",
        token: authActions.getAccessToken() || "",
      };
      ws.send(JSON.stringify(authMessage));
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.at === "auth") {
        setStatus("config");
      }

      if (data.at === "players") {
        const usersMessage = data as PlayersMessage;
        setPlayers(usersMessage.players);
        setSelectedColors([
          ...usersMessage.players.map((player) => player.color),
        ]);
      }

      if (data.at === "start") {
        setStatus("active");
      }

      if (data.at === "update") {
        const updateMessage = data as UpdateMessage;
        batch(() => {
          setData(updateMessage.map);          
          setTurn(updateMessage.turn);         
          setStats([updateMessage.stat]);      
          setCurrentCursor(updateMessage.cursor);
          setPreviousCursor(updateMessage.prev_cursor);
        });
      }

      if (data.at === "chat") {
        const chatMessage = data as ChatMessage;
        setMessages((messages) => [
          ...messages,
          {
            id: messages.length,
            userId: chatMessage.user_id,
            username: chatMessage.username,
            text: chatMessage.message,
            timestamp: new Date(data.timestamp).toLocaleDateString(),
          },
        ]);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setErrorMessage("Что-то пошло не так");
      setStatus("error");
    };

    ws.onclose = (event) => {
      if (event.code === 1008) {
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          console.log(
            `Попытка переподключения ${reconnectAttempts + 1} из ${MAX_RECONNECT_ATTEMPTS}`
          );
          setStatus("connecting");
          reconnectAttempts++;
          setTimeout(connectWebSocket, RECONNECT_DELAY);
        } else {
          console.log("Достигнуто максимальное количество попыток");
          setStatus("error");
          setErrorMessage("Не удалось подключиться к серверу");
        }
      } else {
        setStatus("error");
        setErrorMessage(getWebSocketErrorMessage(event.code));
      }
    };

    return ws;
  };

  createEffect(() => {
    const ws = connectWebSocket();

    onCleanup(() => {
      if (ws) {
        ws.close();
      }
    });
  });

  const handleCursorMove = (move: CursorMove) => {
    socket()?.send(
      JSON.stringify({
        at: "move",
        previous: move.previous,
        current: move.current,
      })
    );
  };

  const handleSendMessage = (text: string) => {
    socket()?.send(JSON.stringify(makeMessage(text)));
  };

  const handleReady = () => {
    socket()?.send(JSON.stringify(makeMessage("I am ready")));
    const readyMessage: ReadyMessage = {
      at: "ready",
    };
    socket()?.send(JSON.stringify(readyMessage));
  };

  const handleCellClick = (rowIndex: number, colIndex: number, cell: Cell) => {
    if (
      (cell.type === "field" || cell.type === "king") &&
      cell.player === userStore.user.user_id
    ) {
      const newCursor = { row: rowIndex, col: colIndex };

      socket()?.send(
        JSON.stringify({
          at: "cursor",
          cursor: newCursor,
        })
      );
    }
  };

  return (
    <div class="container mx-auto p-4 flex flex-col items-center">
      {status() !== "connecting" && status() !== "error" && (
        <Chat messages={messages()} onSendMessage={handleSendMessage} />
      )}

      {status() === "connecting" && <LoadingSpinner />}

      {status() === "config" && (
        <div class="w-full max-w-md">
          <ShareLink />
          <PlayersList
            players={players()}
            currentUserId={userStore.user.user_id}
            onReady={handleReady}
          />
          <ColorSelector
            selectedIndices={selectedColors()}
            onColorSelect={handleColorSelect}
          />
          {showTutorial() && (
            <TutorialPopup onClose={() => setShowTutorial(false)} />
          )}
        </div>
      )}

      {status() === "active" && data() !== undefined && (
        <div class="flex flex-col items-center gap-8">
          <GameStats turn={turn()} stats={stats()} />
          <GameBoard
            data={data()}
            players={players()}
            currentUserId={userStore.user.user_id}
            gameCursor={currentCursor()}
            previousCursor={previousCursor()}
            onCellClick={handleCellClick}
            onCursorMove={handleCursorMove}
          />
        </div>
      )}

      {status() === "error" && <ErrorMessage message={errorMessage()} />}
    </div>
  );
}
