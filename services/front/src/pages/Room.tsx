import { useParams } from '@solidjs/router';
import { createSignal, createEffect, onCleanup } from 'solid-js';
import { authActions } from '../stores/authStore';
import { userStore } from "../stores/userStore";
import { Chat } from "../components/Chat";
import { ColorSelector } from "../components/ColorSelector"
import { ShareLink } from "../components/ShareLink"
import { PlayersList } from "../components/PlayersList"
import { ErrorMessage } from "../components/ErrorMessage"
import { LoadingSpinner } from "../components/LoadingSpinner"
import { GameBoard } from "../components/GameBoard";
import { GameStats } from "../components/GameStats";
import type { Player, CursorMove } from "../types/room"
import type { PlayerData, GameStat } from "../types/map"
import type { Cell } from "../types/map";
import { PlayersMessage, AuthMessage, ChatMessage, ReadyMessage, UpdateMessage} from "../types/messages"


type Status = 'connecting' | 'config' | 'active' | 'error';
type TableData = Cell[][];


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
  const [status, setStatus] = createSignal<Status>('connecting');
  const [players, setPlayers] = createSignal<Player[]>([]);
  const [data, setData] = createSignal<TableData>([[]])
  const [socket, setSocket] = createSignal<WebSocket | null>(null);
  const [messages, setMessages] = createSignal<ChatLine[]>([]);
  const [selectedColors, setSelectedColors] = createSignal<number[]>([]);
  const [turn, setTurn] = createSignal(0);
  const [stats, setStats] = createSignal<[PlayerData, GameStat][]>([]);


  const handleColorSelect = (colorIndex: number) => {
    socket()?.send(JSON.stringify({
      at: "color",
      color: colorIndex
    }));
  };

  createEffect(() => {
    if (userStore.user.username === '') return 

    const getParams = new URLSearchParams({
      user_id: userStore.user.user_id.toString(),
      username: userStore.user.username,
    });
    const ws = new WebSocket(`ws://kingdoms-game.ru/ws/rooms/${params.roomId}/?${getParams.toString()}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      const authMessage: AuthMessage = {
        at: "auth",
        token: authActions.getAccessToken() || '',
      };
      ws.send(JSON.stringify(authMessage));
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.at === 'auth') {
        setStatus('config');
      }

      if (data.at === 'players') {
        const usersMessage = data as PlayersMessage;
        setPlayers(usersMessage.players);
        setSelectedColors([...usersMessage.players.map(player => player.color)]);
      }

      if (data.at === 'start') {
        setStatus('active');
      }

      if (data.at === 'update') {
        const updateMessage = data as UpdateMessage;
        setData(data.map);
        setTurn(updateMessage.turn);
        setStats([updateMessage.stat])
      }

      if (data.at === 'chat') {
        const chatMessage = data as ChatMessage;
        setMessages(messages => [...messages, {
          id: messages.length,
          userId: chatMessage.user_id,
          username: chatMessage.username,
          text: chatMessage.message,
          timestamp: new Date(data.timestamp).toLocaleDateString(),
        }]);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('error');
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event);
      // if (!event.wasClean) {
        setStatus('error');
      // }
    };

    onCleanup(() => {
      if (ws) {
        ws.close();
        console.log("WebSocket закрыт при cleanup");
      }
    });
  });

  const handleCursorMove = (move: CursorMove) => {
    socket()?.send(JSON.stringify({'at': 'move', previous: move.previous, current: move.current}));
  };

  const handleSendMessage = (text: string) => {
    socket()?.send(JSON.stringify(makeMessage(text)));
  };

  const handleReady = () => {
    socket()?.send(JSON.stringify(makeMessage('I am ready')));
    const readyMessage: ReadyMessage = {
      at: "ready",
    };
    socket()?.send(JSON.stringify(readyMessage));
  };

  const handleCellClick = (rowIndex: number, colIndex: number, cell: Cell) => {
    if ((cell.type === 'field' || cell.type === 'king') && 
        cell.player === userStore.user.user_id) {
      const newCursor = { row: rowIndex, col: colIndex };
      
      socket()?.send(JSON.stringify({
        at: 'cursor',
        cursor: newCursor
      }));
    }
  };


  return (
    <div class="container mx-auto p-4 flex flex-col items-center">
      {status() !== 'connecting' && status() !== 'error' && (
        <Chat
          messages={messages()}
          onSendMessage={handleSendMessage}
        />
      )}

      {status() === 'connecting' && (
        <LoadingSpinner/>
      )}


      {status() === 'config' && (
        <div class="w-full max-w-md">
          <ShareLink />
          <PlayersList players={players()} currentUserId={userStore.user.user_id} onReady={handleReady}/>
          <ColorSelector selectedIndices={selectedColors()} onColorSelect={handleColorSelect}/>
        </div>
      )}

      {status() === 'active' && (
        <div class="flex flex-col items-center gap-8">
          <GameStats 
            turn={turn()}
            stats={stats()}
          />
          <GameBoard 
            data={data()}
            players={players()}
            currentUserId={userStore.user.user_id}
            initialCursor={{ row: 0, col: 0 }}
            onCellClick={handleCellClick}
            onCursorMove={handleCursorMove}
          />
        </div>
      )}

      {status() === 'error' && (
        <ErrorMessage message='Something wrong' />
      )}
    </div>
  );
}