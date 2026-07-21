export const PAGE_SIZE = 10;

const getPaginationItems = (currentPage, totalPages) => {
  if (totalPages <= 5) {
    return Array.from({ length: totalPages }, (_, index) => index + 1);
  }

  const items = [1];
  if (currentPage > 3) items.push("start-ellipsis");

  const start = Math.max(2, currentPage - 1);
  const end = Math.min(totalPages - 1, currentPage + 1);
  for (let page = start; page <= end; page += 1) items.push(page);

  if (currentPage < totalPages - 2) items.push("end-ellipsis");
  items.push(totalPages);
  return items;
};

function Pagination({ ariaLabel, currentPage, onPageChange, totalItems }) {
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const activePage = Math.min(currentPage, totalPages);
  const pageStart = (activePage - 1) * PAGE_SIZE;
  const paginationItems = getPaginationItems(activePage, totalPages);

  return (
    <div className="pagination-bar">
      <span>{pageStart + 1}-{Math.min(pageStart + PAGE_SIZE, totalItems)} / {totalItems.toLocaleString()}건</span>
      <nav className="pagination" aria-label={ariaLabel}>
        <button aria-label="이전 페이지" disabled={activePage === 1} type="button" onClick={() => onPageChange(activePage - 1)}>‹</button>
        {paginationItems.map((item) => (
          typeof item === "number" ? (
            <button
              aria-current={item === activePage ? "page" : undefined}
              className={item === activePage ? "active" : ""}
              key={item}
              type="button"
              onClick={() => onPageChange(item)}
            >
              {item}
            </button>
          ) : <span className="pagination-ellipsis" key={item}>…</span>
        ))}
        <button aria-label="다음 페이지" disabled={activePage === totalPages} type="button" onClick={() => onPageChange(activePage + 1)}>›</button>
      </nav>
    </div>
  );
}

export default Pagination;
