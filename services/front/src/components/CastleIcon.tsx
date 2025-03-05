export const CastleIcon = (props: {
  color: string;
  number?: number;
  class?: string;
}) => (
  <div class={`relative flex items-center justify-center ${props.class || ""}`}>
    <svg
      width="32"
      height="33"
      viewBox="0 0 32 33"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M3 32.5H16H29V13.5C29 12.9477 29.4477 12.5 30 12.5H31.8856L31.8857 2.6143C31.8857 1.50973 30.9903 0.614285 29.8857 0.614285H27V5.5C27 6.05228 26.5523 6.5 26 6.5H21C20.4477 6.5 20 6.05228 20 5.5V0.614285H15.8857H12V5.5C12 6.05228 11.5523 6.5 11 6.5H6C5.44772 6.5 5 6.05228 5 5.5V0.535973L2.01439 0.514493C0.904226 0.506505 0 1.40425 0 2.51444V12.5H2C2.55228 12.5 3 12.9477 3 13.5V32.5Z"
        fill="#0369A1"
      />
    </svg>
    {props.number !== undefined && (
      <span class="absolute text-white font-bold text-sm">{props.number}</span>
    )}
  </div>
);
