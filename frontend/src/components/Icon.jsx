const paths = {
  boxes: (
    <>
      <path d="m12 2 8 4.5v9L12 20l-8-4.5v-9L12 2Z" />
      <path d="m4.3 6.7 7.7 4.4 7.7-4.4M12 11.1V20M8 4.3l8 4.6" />
    </>
  ),
  inventory: (
    <>
      <path d="M4 7.5h16v12H4zM7 4h10l2 3.5H5L7 4Z" />
      <path d="M9 12h6M9 15.5h4" />
    </>
  ),
  inbound: (
    <>
      <path d="M4 13v7h16v-7M12 3v12" />
      <path d="m7.5 10.5 4.5 4.5 4.5-4.5" />
    </>
  ),
  outbound: (
    <>
      <path d="M4 11v9h16v-9M12 16V3" />
      <path d="m7.5 7.5 4.5-4.5 4.5 4.5" />
    </>
  ),
  logout: (
    <>
      <path d="M10 5H5v14h5M14 8l4 4-4 4M8 12h10" />
    </>
  ),
  search: <path d="m20 20-4.2-4.2M18 11a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z" />,
  package: (
    <>
      <path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z" />
      <path d="m4.3 7.7 7.7 4.4 7.7-4.4M12 12.1V21" />
    </>
  ),
  location: (
    <>
      <path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z" />
      <circle cx="12" cy="10" r="2.2" />
    </>
  ),
  chart: (
    <>
      <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />
    </>
  ),
  arrow: <path d="M5 12h14M14 7l5 5-5 5" />,
  check: <path d="m5 12 4 4L19 6" />,
  alert: (
    <>
      <path d="M12 3 2.8 20h18.4L12 3Z" />
      <path d="M12 9v4M12 17h.01" />
    </>
  ),
};

function Icon({ name, size = 20 }) {
  return (
    <svg
      aria-hidden="true"
      className="icon"
      fill="none"
      height={size}
      viewBox="0 0 24 24"
      width={size}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
    >
      {paths[name] ?? paths.package}
    </svg>
  );
}

export default Icon;
