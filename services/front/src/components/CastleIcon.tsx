export const CastleIcon = (props: { color: string; number?: number; class?: string; }) => (
  <div class={`relative flex items-center justify-center ${props.class || ''}`}>
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="mx-auto"
    >
    <path 
        fill-rule="evenodd" 
        clip-rule="evenodd" 
        d="M0 28.5972V30C0 31.1046 0.895431 32 2 32H16H29.9856C31.0958 32 31.9935 31.0958 31.9855 29.9856L31.9755 28.5972V28.5972C31.4368 28.5972 31 28.1605 31 27.6217V12.8856C31 12.3965 31.3965 12 31.8856 12V12L31.8857 2.1143C31.8857 1.00973 30.9903 0.114285 29.8857 0.114285H27V2C27 2.55228 26.5523 3 26 3H21C20.4477 3 20 2.55228 20 2V0.114285H15.8857H12V2C12 2.55228 11.5523 3 11 3H6C5.44772 3 5 2.55228 5 2V0.0359707L2.01439 0.0144918C0.904226 0.00650512 0 0.904247 0 2.01444V12V12C0.552285 12 1 12.4477 1 13V27.5972C1 28.1495 0.552285 28.5972 0 28.5972V28.5972Z"
        fill={props.color}
    />
    </svg>
    {props.number !== undefined && (
      <span class="absolute text-white font-bold text-sm">{props.number}</span>
    )}
  </div>
);