import { useEffect, useState } from "react";

import { createOutbound, getOutboundForecast, getOutbounds } from "../api/outbound";
import Icon from "../components/Icon";
import WarehouseLookupModal, { LookupField } from "../components/WarehouseLookupModal";

const emptyForm = { product_id: "", location_id: "", outbound_qty: "" };

function OutboundPage() {
  const [outbounds, setOutbounds] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [forecast, setForecast] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastError, setForecastError] = useState(null);
  const [basisOpen, setBasisOpen] = useState(false);
  const [message, setMessage] = useState(null);
  const [lookupMode, setLookupMode] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);

  const loadOutbounds = async () => {
    const data = await getOutbounds();
    setOutbounds(data);
  };

  const loadForecast = async () => {
    setForecastLoading(true);
    setForecastError(null);

    try {
      const data = await getOutboundForecast();
      setForecast(data);
    } catch (error) {
      console.error(error);
      setForecastError(error.response?.data?.detail ?? "AI forecast is unavailable.");
    } finally {
      setForecastLoading(false);
    }
  };

  useEffect(() => {
    let active = true;

    getOutbounds()
      .then((data) => { if (active) setOutbounds(data); })
      .catch((error) => {
        console.error(error);
        if (active) setMessage({ type: "error", text: "출고 내역을 불러오지 못했습니다." });
      })
      .finally(() => { if (active) setLoading(false); });

    getOutboundForecast()
      .then((data) => { if (active) setForecast(data); })
      .catch((error) => {
        console.error(error);
        if (active) setForecastError(error.response?.data?.detail ?? "AI forecast is unavailable.");
      });

    return () => { active = false; };
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => (
      name === "product_id"
        ? { ...current, product_id: value, location_id: "" }
        : { ...current, [name]: value }
    ));
    if (name === "product_id") {
      setSelectedProduct(null);
      setSelectedLocation(null);
    }
    if (name === "location_id") setSelectedLocation(null);
  };

  const handleApplyProduct = (product) => {
    setForm((current) => ({
      ...current,
      product_id: String(product.product_id),
      location_id: "",
    }));
    setSelectedProduct(product);
    setSelectedLocation(null);
    setLookupMode(null);
  };

  const handleApplyLocation = (location) => {
    setForm((current) => ({ ...current, location_id: String(location.location_id) }));
    setSelectedLocation(location);
    setLookupMode(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);

    try {
      await createOutbound({
        product_id: Number(form.product_id),
        location_id: Number(form.location_id),
        outbound_qty: Number(form.outbound_qty),
      });
      setForm(emptyForm);
      setSelectedProduct(null);
      setSelectedLocation(null);
      await loadOutbounds();
      setMessage({ type: "success", text: "출고가 정상적으로 처리되었습니다." });
    } catch (error) {
      console.error(error);
      setMessage({ type: "error", text: error.response?.data?.detail ?? "출고 처리에 실패했습니다." });
    } finally {
      setSubmitting(false);
    }
  };

  const totalOutbound = outbounds.reduce((sum, item) => sum + item.outbound_qty, 0);

  return (
    <section className="page-stack">
      <div className="page-intro">
        <div><h2>출고 등록 및 내역</h2><p>재고를 확인하고 출고 작업을 안전하게 처리합니다.</p></div>
        <span className="section-tag outbound"><Icon name="outbound" size={16} /> SHIPPING</span>
      </div>

      <div className="operation-layout">
        <article className="form-card">
          <div className="form-card-head">
            <span className="form-card-icon outbound"><Icon name="outbound" /></span>
            <div><h3>새 출고 등록</h3><p>재고 위치와 수량을 확인해 주세요.</p></div>
          </div>

          <form className="operation-form" onSubmit={handleSubmit}>
            <LookupField
              caption={selectedProduct?.product_name}
              label="상품 ID"
              name="product_id"
              placeholder="검색 버튼으로 상품 선택"
              value={form.product_id}
              onChange={handleChange}
              onLookup={() => setLookupMode("product")}
            />
            <LookupField
              caption={selectedLocation ? `${selectedLocation.location_name} · ${selectedLocation.zone} ZONE` : null}
              label="로케이션 ID"
              lookupDisabled={!form.product_id}
              name="location_id"
              placeholder="상품 선택 후 로케이션 검색"
              value={form.location_id}
              onChange={handleChange}
              onLookup={() => setLookupMode("location")}
            />
            <label className="field"><span>출고 수량</span><div className="input-with-unit"><input min="1" name="outbound_qty" placeholder="0" required type="number" value={form.outbound_qty} onChange={handleChange} /><span>EA</span></div></label>

            {message && <div className={`form-message ${message.type}`} role="status"><Icon name={message.type === "success" ? "check" : "alert"} size={18} />{message.text}</div>}

            <button className="primary-button outbound-button" disabled={submitting} type="submit">
              {submitting ? "처리 중..." : "출고 처리"}<Icon name="arrow" size={18} />
            </button>
          </form>
        </article>

        <div className="operation-summary outbound-summary">
          <span>누적 출고 수량</span><strong>{totalOutbound.toLocaleString()}<small> EA</small></strong>
          <p>현재 조회된 출고 기록 {outbounds.length.toLocaleString()}건의 합계입니다.</p>
          <div className="ai-panel">
            <div className="ai-forecast-content">
              <span className="ai-label">AI 오늘 출고량 예측</span>
              <p className="ai-description">과거 출고 패턴과 최근 흐름, 요일·휴일·행사 정보를 분석한 오늘의 예상 출고량입니다.</p>
              {forecast ? (
                <strong>{forecast.predicted_qty.toLocaleString()}<small>EA</small></strong>
              ) : (
                <strong>--<small>EA</small></strong>
              )}
              <small>{forecast ? `예측일 ${forecast.target_date} · 데이터 기준 ${forecast.based_on_date}` : forecastError ?? "오늘 출고량을 예측하고 있습니다."}</small>
            </div>
            <div className="ai-actions">
              <button aria-label="AI 예측 새로고침" disabled={forecastLoading} title="AI 예측 새로고침" type="button" onClick={loadForecast}>
                <Icon name="chart" size={15} />
              </button>
              <button aria-label="AI 예측 근거 보기" disabled={!forecast} title="AI 예측 근거 보기" type="button" onClick={() => setBasisOpen(true)}>
                <Icon name="alert" size={15} />
              </button>
            </div>
          </div>
          <div className="summary-graphic"><Icon name="outbound" size={48} /></div>
        </div>
      </div>

      <article className="data-card">
        <div className="card-toolbar"><div><h3>최근 출고 내역</h3><p>최신 처리 순으로 표시됩니다.</p></div><span className="record-count">{outbounds.length.toLocaleString()} RECORDS</span></div>
        {loading ? <div className="state-message"><Icon name="package" />내역을 불러오는 중입니다.</div> : outbounds.length === 0 ? <div className="state-message"><Icon name="package" />등록된 출고 내역이 없습니다.</div> : (
          <div className="table-wrap"><table><thead><tr><th>출고 번호</th><th>상품 ID</th><th>로케이션</th><th>출고 수량</th><th>처리 상태</th></tr></thead><tbody>
            {outbounds.map((item) => <tr key={item.outbound_id}><td className="mono-cell">OUT-{String(item.outbound_id).padStart(5, "0")}</td><td><span className="item-id">PRD-{String(item.product_id).padStart(4, "0")}</span></td><td><span className="location-cell"><Icon name="location" size={16} /> LOC-{item.location_id}</span></td><td><strong className="quantity outbound-quantity">-{item.outbound_qty.toLocaleString()}</strong><span className="unit"> EA</span></td><td><span className="status-pill success">출고 완료</span></td></tr>)}
          </tbody></table></div>
        )}
      </article>

      {basisOpen && forecast && (
        <ForecastBasisModal forecast={forecast} onClose={() => setBasisOpen(false)} />
      )}

      {lookupMode && (
        <WarehouseLookupModal
          mode={lookupMode}
          productId={form.product_id}
          onApply={lookupMode === "product" ? handleApplyProduct : handleApplyLocation}
          onClose={() => setLookupMode(null)}
        />
      )}
    </section>
  );
}

function ForecastBasisModal({ forecast, onClose }) {
  const basis = forecast.basis ?? {};
  const features = basis.features ?? {};
  const source = basis.source ?? {};
  const notes = basis.notes ?? [];

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <article className="modal-card" role="dialog" aria-modal="true" aria-label="예측근거" onClick={(event) => event.stopPropagation()}>
        <div className="modal-head">
          <div><span>FORECAST BASIS</span><h3>예측근거</h3></div>
          <button type="button" onClick={onClose}>닫기</button>
        </div>
        <div className="basis-grid">
          <div><span>예측일</span><strong>{forecast.target_date}</strong></div>
          <div><span>예측수량</span><strong>{forecast.predicted_qty.toLocaleString()} EA</strong></div>
          <div><span>기준 데이터</span><strong>{basis.based_on_date ?? forecast.based_on_date}</strong></div>
          <div><span>실행 장치</span><strong>{basis.device ?? forecast.device}</strong></div>
        </div>
        <div className="basis-section">
          <h4>입력 지표</h4>
          <dl>
            <div><dt>요일 번호</dt><dd>{features.weekday_num}</dd></div>
            <div><dt>월/일</dt><dd>{features.month}/{features.day}</dd></div>
            <div><dt>주말 여부</dt><dd>{features.is_weekend ? "Y" : "N"}</dd></div>
            <div><dt>행사/프로모션</dt><dd>{features.event}/{features.promo}</dd></div>
            <div><dt>전일 출고량</dt><dd>{Number(features.prev_qty ?? 0).toLocaleString()} EA</dd></div>
            <div><dt>7일 평균</dt><dd>{Number(features.avg7_qty ?? 0).toLocaleString()} EA</dd></div>
            <div><dt>상위 SKU 비율</dt><dd>{features.top_sku_ratio}</dd></div>
            <div><dt>저온/중량 비율</dt><dd>{features.cold_chain_ratio}/{features.heavy_item_ratio}</dd></div>
          </dl>
        </div>
        <div className="basis-section">
          <h4>데이터 기준</h4>
          <p>마지막 기록일 {source.last_recorded_date ?? forecast.based_on_date}, 마지막 출고량 {Number(source.last_recorded_outbound_qty ?? 0).toLocaleString()} EA 기준으로 최근 패턴을 사용했습니다.</p>
          {notes.map((note) => <p key={note}>{note}</p>)}
        </div>
      </article>
    </div>
  );
}

export default OutboundPage;
