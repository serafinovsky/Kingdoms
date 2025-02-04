interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
  text?: string;
}

export function LoadingSpinner({ 
  size = 'medium', 
  showText = true,
  text = 'Загрузка...'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    small: 'w-6 h-6 border-2',
    medium: 'w-8 h-8 border-3',
    large: 'w-12 h-12 border-4'
  };

  return (
    <div class="flex flex-col items-center gap-3">
      <div 
        class={`${sizeClasses[size]} border-sky-600/50 border-t-sky-600 
                rounded-full animate-spin`}
      />
      {showText && (
        <p class="text-sm text-gray-600">{text}</p>
      )}
    </div>
  );
}