import { useEffect, useMemo, useState } from "react";

import { getInventories } from "../api/inventory";
import Icon from "../components/Icon";
import Pagination, { PAGE_SIZE } from "../components/Pagination";

function InventoryPage() {
  const [inventories, setInventories] = useState([]);
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [lowStockOpen, setLowStockOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    getInventories()
      .then((data) => {
        if (active) setInventories(data);
      })
      .catch((requestError) => {
        console.error(requestError);
        if (active) setError("재고 데이터를 불러오지 못했습니다.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const productInventories = useMemo(() => {
    const products = new Map();

    inventories.forEach((item) => {
      const productKey = item.product_id ?? item.product_name;
      const product = products.get(productKey) ?? {
        product_id: item.product_id,
        product_name: item.product_name,
        total_stock_qty: 0,
        location_ids: new Set(),
      };

      product.total_stock_qty += Number(item.stock_qty) || 0;
      product.location_ids.add(item.location_id);
      products.set(productKey, product);
    });

    return Array.from(products.values(), (product) => ({
      ...product,
      location_ids: Array.from(product.location_ids),
    }));
  }, [inventories]);

  const filteredInventories = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) return productInventories;

    return productInventories.filter((item) =>
      [item.product_name, ...item.location_ids]
        .some((value) => String(value).toLowerCase().includes(normalizedQuery)),
    );
  }, [productInventories, query]);

  const totalPages = Math.max(1, Math.ceil(filteredInventories.length / PAGE_SIZE));
  const activePage = Math.min(currentPage, totalPages);
  const pageStart = (activePage - 1) * PAGE_SIZE;
  const paginatedInventories = filteredInventories.slice(pageStart, pageStart + PAGE_SIZE);

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
    setCurrentPage(1);
  };

  const totalStock = inventories.reduce((sum, item) => sum + item.stock_qty, 0);
  const locationCount = new Set(inventories.map((item) => item.location_id)).size;
  const lowStockInventories = inventories.filter((item) => item.stock_qty <= 10);
  const lowStockCount = lowStockInventories.length;

  return (
    <section className="page-stack">
      <div className="page-intro">
        <div>
          <h2>현재 창고 재고</h2>
          <p>상품별 재고와 보관 위치를 실시간으로 확인합니다.</p>
        </div>
        <span className="sync-badge"><span className="status-dot" /> LIVE DATA</span>
      </div>

      <div className="metric-grid">
        <article className="metric-card accent-blue">
          <div className="metric-icon"><Icon name="package" /></div>
          <span>재고 항목</span><strong>{productInventories.length.toLocaleString()}</strong>
          <small>재고가 등록된 상품</small>
        </article>
        <article className="metric-card accent-green">
          <div className="metric-icon"><Icon name="chart" /></div>
          <span>총 보유 수량</span><strong>{totalStock.toLocaleString()}</strong>
          <small>전체 가용 재고</small>
        </article>
        <article className="metric-card accent-violet">
          <div className="metric-icon"><Icon name="location" /></div>
          <span>사용 로케이션</span><strong>{locationCount.toLocaleString()}</strong>
          <small>재고가 배치된 위치</small>
        </article>
        <button
          aria-haspopup="dialog"
          className="metric-card metric-card-button accent-orange"
          disabled={lowStockCount === 0}
          type="button"
          onClick={() => setLowStockOpen(true)}
        >
          <div className="metric-icon"><Icon name="alert" /></div>
          <span>부족 재고</span><strong>{lowStockCount.toLocaleString()}</strong>
          <small>10개 이하 · 클릭하여 로케이션 확인</small>
        </button>
      </div>

      <article className="data-card">
        <div className="card-toolbar">
          <div><h3>재고 목록</h3><p>총 {filteredInventories.length.toLocaleString()}개 상품</p></div>
          <label className="search-box">
            <Icon name="search" size={18} />
            <input
              aria-label="재고 검색"
              placeholder="상품명, 로케이션 ID 검색"
              value={query}
              onChange={handleQueryChange}
            />
          </label>
        </div>

        {error ? <StateMessage type="error" message={error} /> : loading ? (
          <StateMessage message="재고 데이터를 불러오는 중입니다." />
        ) : filteredInventories.length === 0 ? (
          <StateMessage message="표시할 재고가 없습니다." />
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead><tr><th>상품명</th><th>사용 로케이션</th><th>총 재고</th><th>상태</th></tr></thead>
                <tbody>
                  {paginatedInventories.map((item) => (
                    <tr key={item.product_id ?? item.product_name}>
                      <td><span className="item-id">{item.product_name}</span></td>
                      <td><span className="location-cell"><Icon name="location" size={16} /> {item.location_ids.length.toLocaleString()}개 로케이션</span></td>
                      <td><strong className="quantity">{item.total_stock_qty.toLocaleString()}</strong><span className="unit"> EA</span></td>
                      <td><span className={`status-pill ${item.total_stock_qty <= 10 ? "warning" : "success"}`}>{item.total_stock_qty <= 10 ? "재고 부족" : "정상"}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination ariaLabel="재고 목록 페이지" currentPage={activePage} totalItems={filteredInventories.length} onPageChange={setCurrentPage} />
          </>
        )}
      </article>

      {lowStockOpen && (
        <LowStockModal inventories={lowStockInventories} onClose={() => setLowStockOpen(false)} />
      )}
    </section>
  );
}

function LowStockModal({ inventories, onClose }) {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(inventories.length / PAGE_SIZE));
  const activePage = Math.min(currentPage, totalPages);
  const pageStart = (activePage - 1) * PAGE_SIZE;
  const rows = inventories.slice(pageStart, pageStart + PAGE_SIZE);

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <article className="modal-card low-stock-modal" role="dialog" aria-modal="true" aria-label="부족 재고 로케이션" onClick={(event) => event.stopPropagation()}>
        <div className="modal-head">
          <div><span>LOW STOCK LOCATIONS</span><h3>부족 재고 로케이션</h3></div>
          <button type="button" onClick={onClose}>닫기</button>
        </div>
        <div className="low-stock-summary">
          <span className="low-stock-summary-icon"><Icon name="alert" size={18} /></span>
          <p>현재 재고가 10개 이하인 상품·로케이션만 표시합니다. <strong>총 {inventories.length.toLocaleString()}건</strong></p>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>상품명</th><th>로케이션</th><th>현재 재고</th><th>상태</th></tr></thead>
            <tbody>
              {rows.map((item) => (
                <tr key={item.inventory_id}>
                  <td><span className="item-id">{item.product_name}</span></td>
                  <td><span className="location-cell"><Icon name="location" size={16} /> LOC-{item.location_id}</span></td>
                  <td><strong className="quantity">{item.stock_qty.toLocaleString()}</strong><span className="unit"> EA</span></td>
                  <td><span className="status-pill warning">재고 부족</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Pagination ariaLabel="부족 재고 로케이션 페이지" currentPage={activePage} totalItems={inventories.length} onPageChange={setCurrentPage} />
      </article>
    </div>
  );
}

function StateMessage({ message, type = "default" }) {
  return <div className={`state-message ${type}`}><Icon name={type === "error" ? "alert" : "package"} />{message}</div>;
}

export default InventoryPage;
