const paths = {
  arrow: "M5 12h14m-6-6 6 6-6 6",

  box: "m12 3 9 5-9 5-9-5 9-5Zm-9 5v9l9 5 9-5V8M12 13v9",

  tools:
    "m14 6 4-4a6 6 0 0 1-7 8L4 17a2 2 0 0 0 3 3l7-7a6 6 0 0 0 8-7l-4 4-4-4Z",

  eye: "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Zm10-3a3 3 0 1 0 0 6 3 3 0 0 0 0-6",

  receipt:
    "M5 3v18l3-2 4 2 4-2 3 2V3l-3 2-4-2-4 2-3-2Zm4 6h6m-6 4h6",

  shield:
    "m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Zm-4 9 3 3 5-6",

  document:
    "M14 3H5v18h14V8l-5-5Zm0 0v5h5M8 12h8m-8 4h6",

  grid:
    "M3 3h7v7H3V3Zm11 0h7v7h-7V3ZM3 14h7v7H3v-7Zm11 0h7v7h-7v-7Z",

  voice:
    "M9 5a3 3 0 0 1 6 0v7a3 3 0 0 1-6 0V5Zm-4 6v1a7 7 0 0 0 14 0v-1M12 19v3m-4 0h8",

  balance:
    "M12 3v18M5 7h14M8 21h8M5 7l-4 8h8L5 7Zm14 0-4 8h8l-4-8Z",

  book:
    "M12 5C8 2 4 3 2 4v16c4-2 7-1 10 1m0-16c4-3 8-2 10-1v16c-4-2-7-1-10 1V5Z",

  sound:
    "m3 9 5 0 5-5v16l-5-5H3V9Zm14-2a7 7 0 0 1 0 10m3-13a11 11 0 0 1 0 16",

  search:
    "M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14Zm5 12 6 6",

  check: "m5 12 4 4L19 6",

  compass:
    "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm4 6-2 6-6 2 2-6 6-2Z",
};

export default function Icon({ name, size = 22 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name] || paths.book} />
    </svg>
  );
}