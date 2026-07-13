import { useEffect, useMemo, useState } from "react";

import { getLocationOptions, getProducts } from "../api/catalog";
import Icon from "./Icon";

export function LookupField({
  label,
  name,
  value,
  placeholder,
  onChange,
  onLookup,
  lookupDisabled = false,
  caption,
}) {
  return (
    <label className="field lookup-field">
      <span>{label}</span>
      <div className="lookup-input">
        <input
          min="1"
          name={name}
          placeholder={placeholder}
          required
          type="number"
          value={value}
          onChange={onChange}
        />
        <button
          aria-label={`${label} 검색`}
          disabled={lookupDisabled}
          title={lookupDisabled ? "상품을 먼저 선택해 주세요" : `${label} 검색`}
          type="button"
          onClick={onLookup}
        >
          <Icon name="search" size={17} />
        </button>
      </div>
      {caption && <small className="lookup-caption">{caption}</small>}
    </label>
  );
}

function WarehouseLookupModal({ mode, productId, onApply, onClose }) {
  const [items, setItems] = useState([]);
  const [source, setSource] = useState(null);
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const request = mode === "product"
      ? getProducts().then((data) => ({ items: data, source: "products" }))
      : getLocationOptions(Number(productId));

    request
      .then((data) => {
        if (!active) return;
        setItems(data.items);
        setSource(data.source);
      })
      .catch((requestError) => {
        console.error(requestError);
        if (active) setError("검색 정보를 불러오지 못했습니다.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  }, [mode, productId]);

  const filteredItems = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) return items;

    return items.filter((item) => {
      if (mode === "product") {
        return [item.product_id, item.product_name, item.barcode, item.category]
          .some((value) => String(value ?? "").toLowerCase().includes(normalizedQuery));
      }

      return [item.location_id, item.location_name, item.zone]
        .some((value) => String(value ?? "").toLowerCase().includes(normalizedQuery));
    });
  }, [items, mode, query]);

  const selectedItem = items.find((item) => (
    mode === "product" ? item.product_id : item.location_id
  ) === selectedId);

  const title = mode === "product" ? "상품 검색" : "로케이션 선택";
  const description = mode === "product"
    ? "상품 이름을 검색하고 적용할 상품을 선택하세요."
    : source === "product_stock"
      ? "선택한 상품의 재고가 있는 로케이션입니다."
      : "선택한 상품의 재고 로케이션이 없어 빈 로케이션을 표시합니다.";

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <article
        aria-label={title}
        aria-modal="true"
        className="modal-card lookup-modal"
        role="dialog"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-head">
          <div><span>WAREHOUSE LOOKUP</span><h3>{title}</h3></div>
          <button type="button" onClick={onClose}>닫기</button>
        </div>

        <div className="lookup-modal-body">
          <p className="lookup-description">{description}</p>
          <label className="search-box lookup-search">
            <Icon name="search" size={17} />
            <input
              autoFocus
              placeholder={mode === "product" ? "상품 이름을 입력하세요" : "로케이션 이름 또는 존 검색"}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>

          <div className="lookup-list" role="listbox" aria-label={`${title} 결과`}>
            {loading ? (
              <div className="state-message"><Icon name="package" />검색 정보를 불러오는 중입니다.</div>
            ) : error ? (
              <div className="state-message error"><Icon name="alert" />{error}</div>
            ) : filteredItems.length === 0 ? (
              <div className="state-message"><Icon name="search" />조건에 맞는 항목이 없습니다.</div>
            ) : filteredItems.map((item) => {
              const id = mode === "product" ? item.product_id : item.location_id;
              const selected = selectedId === id;

              return (
                <button
                  aria-selected={selected}
                  className={`lookup-row${selected ? " selected" : ""}`}
                  key={id}
                  role="option"
                  type="button"
                  onClick={() => setSelectedId(id)}
                  onDoubleClick={() => onApply(item)}
                >
                  <span className="lookup-row-id">
                    {mode === "product" ? `PRD-${String(id).padStart(4, "0")}` : `LOC-${id}`}
                  </span>
                  <span className="lookup-row-main">
                    <strong>{mode === "product" ? item.product_name : item.location_name}</strong>
                    <small>
                      {mode === "product"
                        ? `${item.category} · ${item.barcode}`
                        : `${item.zone} ZONE · ${source === "product_stock" ? `재고 ${item.stock_qty.toLocaleString()} EA` : "빈 로케이션"}`}
                    </small>
                  </span>
                  <span className={`lookup-state ${source === "product_stock" ? "stocked" : ""}`}>
                    {selected ? "선택됨" : mode === "product" ? "선택" : source === "product_stock" ? "재고 있음" : "비어 있음"}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="lookup-modal-actions">
          <button className="secondary-button" type="button" onClick={onClose}>취소</button>
          <button
            className="primary-button"
            disabled={!selectedItem}
            type="button"
            onClick={() => onApply(selectedItem)}
          >
            적용 <Icon name="check" size={17} />
          </button>
        </div>
      </article>
    </div>
  );
}

export default WarehouseLookupModal;
