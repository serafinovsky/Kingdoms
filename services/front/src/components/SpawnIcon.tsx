export const SpawnIcon = (props: { color: string; number?: number; class?: string; }) => (
  <div class={`relative flex items-center justify-center ${props.class || ''}`}>
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="16" cy="16" r="16" fill={props.color}/>
    </svg>
    {props.number !== undefined && (
      <span class="absolute text-white font-bold text-sm">{props.number}</span>
    )}
  </div>
);
