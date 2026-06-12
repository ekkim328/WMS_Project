import { useEffect, useMemo, useState } from "react";

import { getInventories } from "../api/inventory";
import Icon from "../components/Icon";

function InventoryPage() {
  const [inventories, setInventories] = useState([]);
  const [query, setQuery] = useState("");
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

  const filteredInventories = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) return inventories;

    return inventories.filter((item) =>
      [item.inventory_id, item.product_id, item.location_id]
        .some((value) => String(value).toLowerCase().includes(normalizedQuery)),
    );
  }, [inventories, query]);

  const totalStock = inventories.reduce((sum, item) => sum + item.stock_qty, 0);
  const locationCount = new Set(inventories.map((item) => item.location_id)).size;
  const lowStockCount = inventories.filter((item) => item.stock_qty <= 10).length;

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
          <span>재고 항목</span><strong>{inventories.length.toLocaleString()}</strong>
          <small>등록된 상품·위치 조합</small>
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
        <article className="metric-card accent-orange">
          <div className="metric-icon"><Icon name="alert" /></div>
          <span>부족 재고</span><strong>{lowStockCount.toLocaleString()}</strong>
          <small>10개 이하 재고 항목</small>
        </article>
      </div>

      <article className="data-card">
        <div className="card-toolbar">
          <div><h3>재고 목록</h3><p>총 {filteredInventories.length.toLocaleString()}건</p></div>
          <label className="search-box">
            <Icon name="search" size={18} />
            <input
              aria-label="재고 검색"
              placeholder="상품, 로케이션 ID 검색"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
        </div>

        {error ? <StateMessage type="error" message={error} /> : loading ? (
          <StateMessage message="재고 데이터를 불러오는 중입니다." />
        ) : filteredInventories.length === 0 ? (
          <StateMessage message="표시할 재고가 없습니다." />
        ) : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>재고 ID</th><th>상품 ID</th><th>로케이션</th><th>현재 재고</th><th>상태</th></tr></thead>
              <tbody>
                {filteredInventories.map((item) => (
                  <tr key={item.inventory_id}>
                    <td className="mono-cell">#{String(item.inventory_id).padStart(4, "0")}</td>
                    <td><span className="item-id">PRD-{String(item.product_id).padStart(4, "0")}</span></td>
                    <td><span className="location-cell"><Icon name="location" size={16} /> LOC-{item.location_id}</span></td>
                    <td><strong className="quantity">{item.stock_qty.toLocaleString()}</strong><span className="unit"> EA</span></td>
                    <td><span className={`status-pill ${item.stock_qty <= 10 ? "warning" : "success"}`}>{item.stock_qty <= 10 ? "재고 부족" : "정상"}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}

function StateMessage({ message, type = "default" }) {
  return <div className={`state-message ${type}`}><Icon name={type === "error" ? "alert" : "package"} />{message}</div>;
}

export default InventoryPage;
