export const CastleIcon = (props: {
  color: string;
  number?: number;
  class?: string;
}) => (
  <div class={`relative flex items-center justify-center ${props.class || ""}`}>
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path fill-rule="evenodd" clip-rule="evenodd" d="M0 28.5972V30C0 31.1046 0.895431 32 2 32H16H29.9856C31.0958 32 31.9935 31.0958 31.9855 29.9856L31.9755 28.5972L31.8856 12L31.8857 2.1143C31.8857 1.00973 30.9903 0.114285 29.8857 0.114285H27V4C27 4.55228 26.5523 5 26 5H21C20.4477 5 20 4.55228 20 4V0.114285H15.8857H12V4C12 4.55228 11.5523 5 11 5H6C5.44772 5 5 4.55229 5 4V0.0359707L2.01439 0.014492C0.904226 0.00650597 0 0.904247 0 2.01444V12V28.5972Z" fill={props.color}/>
    </svg>
    {props.number !== undefined && (
      <span class="absolute text-white font-bold text-sm">{props.number}</span>
    )}
  </div>
);
