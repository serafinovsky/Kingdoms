export const KingIcon = (props: { color: string; number?: number; class?: string; }) => (
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
        d="M2 32C0.895431 32 0 31.1046 0 30V16V0C0 0 3.21336 2.89444 5 5C6.72843 7.03696 9 10.5493 9 10.5493C9 10.5493 10.6631 7.65581 12 6C13.3594 4.31626 15.8857 2.04932 15.8857 2.04932C15.8857 2.04932 18.579 4.28455 20 6C21.3576 7.6389 23 10.5493 23 10.5493C23 10.5493 25.2697 7.03535 27 5C28.7477 2.9442 32 0 32 0L31.8857 16.1143L31.9855 29.9856C31.9935 31.0958 31.0958 32 29.9856 32H16H2Z"
        fill={props.color}
      />
    </svg>
    {props.number !== undefined && (
      <span class="absolute text-white font-bold text-sm">{props.number}</span>
    )}
  </div>
);