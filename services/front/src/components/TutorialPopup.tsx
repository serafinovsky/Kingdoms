import { Component, createSignal, JSX, createMemo } from "solid-js";
import { KingIcon } from "./KingIcon";
import { CastleIcon } from "./CastleIcon";
import { FieldIcon } from "./FieldIcon";
import { CellType } from "../types/map";

type TutorialPage = {
  title: string;
  content: JSX.Element;
  image?: string;
};

export const TutorialPopup: Component<{ onClose: () => void }> = (props) => {
  const [currentPage, setCurrentPage] = createSignal(0);

  const getColor = createMemo(() => (cellType: CellType) => {
    switch (cellType) {
      case CellType.BLOCKER:
        return '#71717a';
      case CellType.CASTLE:
        return '#0369A1';
      case CellType.KING:
        return '#0369A1';
      default:
        return '#d4d4d8';
    }
  });

  const tutorialPages: TutorialPage[] = [
    {
      title: "Добро пожаловать в Kingdoms!",
      content: (
        <div class="space-y-4">
          <p class="text-gray-600">
            Kingdoms - это пошаговая стратегия, где вам предстоит расширять свои владения 
            и захватывать территории противников.
          </p>
        </div>
      )
    },
    {
      title: "Ваш Король",
      content: (
        <div class="space-y-4">
          <p>
            Король - ваша главная фигура. Вы начинаете игру с одним королём 
            и при его захвате игра для вас прекращется.
          </p>
          <div class="flex items-center gap-2">
            <KingIcon color={getColor()(CellType.KING)} class='w-7 h-7' />
            <span class="text-sm text-gray-600">- Ваш король</span>
          </div>
        </div>
      )
    },
    {
      title: "Что есть на карте",
      content: (
        <div class="space-y-4">
          <p>
            Не королем единым. На карте есть несколько типов клеток, 
            каждая из которых имеет свои особенности.
          </p>
          <div class="flex items-center gap-2">
            <CastleIcon color={getColor()(CellType.CASTLE)} class='w-7 h-7' />
            <span class="text-sm text-gray-600">- Замок, генерирует очки каждый ход</span>
          </div>
          <div class="flex items-center gap-2">
            <FieldIcon color={getColor()(CellType.BLOCKER)} class='w-7 h-7' />
            <span class="text-sm text-gray-600">
              - Препятствие. На эту клетку нельзя переместить армию
            </span>
          </div>
          <div class="flex items-center gap-2">
            <FieldIcon color={getColor()(CellType.FIELD)} class='w-7 h-7' />
            <span class="text-sm text-gray-600">- Обычная клетка</span>
          </div>
          <div class="text-sm text-gray-600 mt-3">
            Клетки могут принадлежать противнику, в этом случае для их захвата 
            численость вашей армии должна быть больше
          </div>
          <div class="flex items-center gap-2">
            <FieldIcon color='#D97706' number={7} class='w-7 h-7' />
            <CastleIcon color='#D97706' number={7} class='w-7 h-7' />
            <KingIcon color='#D97706' number={7} class='w-7 h-7' />
          </div>
        </div>
      )
    },
    {
      title: "Ходы",
      content: (
        <div class="space-y-4">
          <p>
            Для захвата клеток вам нужно перемещать армии.
          </p>
          <p>
            Кликните мышью на свою клетку и перемещайте курсор стрелками клавиатуры, 
            чтобы выбрать направление атаки.
          </p>
          <div class="flex justify-center gap-2 my-4">
            {['←', '↑', '↓', '→'].map((key) => (
              <kbd class="px-3 py-1.5 bg-white/80 rounded-lg text-sm border border-gray-200 shadow-sm">
                {key}
              </kbd>
            ))}
          </div>
          <p>
            Ваша армия может перемещаться только на одну клетку за ход, но вы можете 
            построить план переместив свой курсор на несколько клеток, в этом случае 
            армии каждый последующий ход будут перемещаться по выбраному вами маршруту.
          </p>
          <p>
            Если ваша стратегия изменилась, просто нажмите <kbd class="px-2 py-1 
            bg-white/80 rounded-lg text-sm border border-gray-200 shadow-sm">Esc</kbd> и 
            можете планировать новую атаку
          </p>
        </div>
      )
    }
  ];

  const nextPage = () => {
    if (currentPage() < tutorialPages.length - 1) {
      setCurrentPage(p => p + 1);
    } else {
      props.onClose();
      localStorage.setItem('kingdomsTutorialSeen', 'true');
    }
  };

  const prevPage = () => {
    if (currentPage() > 0) {
      setCurrentPage(p => p - 1);
    }
  };

  return (
    <div class="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
      <div class="bg-white/90 backdrop-blur-sm p-6 rounded-2xl shadow-xl 
                  border border-white/20 w-full max-w-lg">
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-gray-800 mb-4">
            {tutorialPages[currentPage()].title}
          </h2>
          <div class="text-gray-600">
            {tutorialPages[currentPage()].content}
          </div>
        </div>
        
        <div class="flex justify-between items-center">
          <button
            onClick={prevPage}
            class="px-4 py-2 rounded-xl text-sm font-medium
                   disabled:opacity-50 disabled:cursor-not-allowed
                   hover:bg-gray-100 active:scale-95 transition-all"
            disabled={currentPage() === 0}
          >
            Назад
          </button>
          
          <div class="flex gap-1.5">
            {tutorialPages.map((_, index) => (
              <div
                class={`w-2 h-2 rounded-full transition-colors
                        ${index === currentPage() 
                          ? 'bg-sky-700' 
                          : 'bg-gray-300'}`}
              />
            ))}
          </div>

          <button
            onClick={nextPage}
            class="px-4 py-2 bg-sky-700 text-white rounded-xl 
                   text-sm font-medium shadow-lg shadow-sky-500/10
                   hover:bg-sky-600 active:scale-95 transition-all"
          >
            {currentPage() === tutorialPages.length - 1 ? 'Начать игру' : 'Далее'}
          </button>
        </div>
      </div>
    </div>
  );
};