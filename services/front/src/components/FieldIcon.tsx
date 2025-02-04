export const FieldIcon = (props: { color: string; number?: number; class?: string; }) => (
  <div class={`relative flex items-center justify-center ${props.class || ''}`}>
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="mx-auto"
    >
      <path 
        d="M0 16V30C0 31.1046 0.895431 32 2 32H16H29.9856C31.0958 32 31.9935 31.0958 31.9855 29.9856L31.8857 16.1143V2.11429C31.8857 1.00972 30.9903 0.114286 29.8857 0.114286H15.8857L2.01439 0.0144921C0.904223 0.00650524 0 0.904248 0 2.01444V16Z" 
        fill={props.color}
      />
    </svg>
    {/* <div class="w-8 h-8 rounded-sm" style={{ background: props.color }}>
    </div> */}
    {props.number !== undefined && (
      <span class="absolute text-white font-bold text-sm">{props.number}</span>
    )}
  </div>
);
