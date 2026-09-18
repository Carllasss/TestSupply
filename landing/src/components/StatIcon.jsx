const paths = {
  clock: <><circle cx="12" cy="12" r="8.5" /><path d="M12 7.5V12l3 2" /></>,
  spark: <path d="M12 3l2.1 5.9L20 11l-5.9 2.1L12 19l-2.1-5.9L4 11l5.9-2.1L12 3z" />,
  layers: <><path d="M12 3l8 4.5-8 4.5-8-4.5L12 3z" /><path d="M4 12.5l8 4.5 8-4.5" /><path d="M4 16.5l8 4.5 8-4.5" /></>,
  code: <><path d="M8 6L2.5 12 8 18" /><path d="M16 6l5.5 6-5.5 6" /></>,
}

export function StatIcon({ name }) {
  return (
    <svg
      className="stat-card__icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths[name]}
    </svg>
  )
}
