import { For } from 'solid-js';
import { COLORS } from '../config';

type ColorSelectorProps = {
  selectedIndices: number[];
  onColorSelect: (index: number) => void;
};

export const ColorSelector = (props: ColorSelectorProps) => {
  console.log(props, props.selectedIndices)

  const handleColorClick = (index: number) => {
    if (!props.selectedIndices.includes(index)) {
      props.onColorSelect(index);
    }
  };

  return (
    <div class="mb-8 w-full max-w-2xl mx-auto">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">Выберите цвет</h2>
      <div class="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-xl 
                  border border-white/20 hover:shadow-2xl transition-all duration-300">
        <div class="flex flex-wrap gap-4 justify-center">
          <For each={COLORS}>
            {(color, index) => {
              return (
                <div class="relative group">
                  <button 
                    class={`w-14 h-14 rounded-xl transition-all duration-300
                           ${props.selectedIndices.includes(index()) 
                             ? 'cursor-not-allowed grayscale opacity-50' 
                             : 'hover:scale-110 hover:shadow-lg focus:ring-2 focus:ring-sky-700/30'}
                           shadow-lg backdrop-blur-sm`}
                    style={{ 
                      "background-color": color,
                      "box-shadow": props.selectedIndices.includes(index()) 
                        ? 'none' 
                        : `0 4px 12px ${color}40`
                    }}
                    onClick={() => handleColorClick(index())}
                    disabled={props.selectedIndices.includes(index())}
                    aria-label={`Color ${index() + 1}${props.selectedIndices.includes(index()) ? ' (selected)' : ''}`}
                  />
                  {/* {props.selectedIndices.includes(index()) ? (
                    <div class="absolute inset-0 flex items-center justify-center" onClick={() => alert(1)}>
                      <div class="w-8 h-8 rounded-full bg-white/90 backdrop-blur-sm 
                                flex items-center justify-center shadow-inner">
                        <svg 
                          class="w-5 h-5 text-gray-400" 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path 
                            stroke-linecap="round" 
                            stroke-linejoin="round" 
                            stroke-width="2" 
                            d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      </div>
                    </div>
                  ) : (
                    <div class="absolute -inset-1 bg-white/10 rounded-xl scale-90 opacity-0 
                               group-hover:scale-100 group-hover:opacity-100 transition-all duration-300" />
                  )} */}
                </div>
              );
            }}
          </For>
        </div>
        
        <div class="mt-6 text-sm text-gray-600 text-center bg-gray-50/50 
                    backdrop-blur-sm rounded-xl p-3 border border-gray-100/20">
          <p>Выберите цвет для своего королевства</p>
          <p class="text-gray-400 text-xs mt-1">Серые цвета уже выбраны другими игроками</p>
        </div>
      </div>
    </div>
  );
};