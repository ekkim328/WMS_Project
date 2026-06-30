import { useEffect, useState } from "react";

import { createInbound, getInboundForecast, getInboundLocationRecommendation, getInbounds } from "../api/inbound";
import Icon from "../components/Icon";

const emptyForm = { product_id: "", location_id: "", inbound_qty: "" };

function InboundPage() {
  const [inbounds, setInbounds] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [forecast, setForecast] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastError, setForecastError] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [recommendationError, setRecommendationError] = useState(null);
  const [message, setMessage] = useState(null);

  const loadInbounds = async () => {
    const data = await getInbounds();
    setInbounds(data);
  };

  useEffect(() => {
    let active = true;

    getInbounds()
      .then((data) => {
        if (active) setInbounds(data);
      })
      .catch((error) => {
        console.error(error);
        if (active) setMessage({ type: "error", text: "입고 내역을 불러오지 못했습니다." });
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    if (name === "product_id") {
      setForecast(null);
      setForecastError(null);
    }
    if (name === "product_id" || name === "inbound_qty") {
      setRecommendation(null);
      setRecommendationError(null);
    }
  };

  const handleForecastInbound = async () => {
    setForecastLoading(true);
    setForecastError(null);
    setMessage(null);

    try {
      const data = await getInboundForecast({
        product_id: Number(form.product_id),
      });
      setForecast(data);
    } catch (error) {
      console.error(error);
      setForecastError(error.response?.data?.detail ?? "AI inbound forecast is unavailable.");
    } finally {
      setForecastLoading(false);
    }
  };

  const handleApplyForecast = () => {
    if (!forecast) return;
    setForm((current) => ({ ...current, inbound_qty: String(forecast.predicted_qty) }));
  };

  const handleRecommendLocation = async () => {
    setRecommendationLoading(true);
    setRecommendationError(null);
    setMessage(null);

    try {
      const data = await getInboundLocationRecommendation({
        product_id: Number(form.product_id),
        inbound_qty: Number(form.inbound_qty),
      });
      setRecommendation(data);
      setForm((current) => ({ ...current, location_id: String(data.location_id) }));
    } catch (error) {
      console.error(error);
      setRecommendationError(error.response?.data?.detail ?? "AI recommendation is unavailable.");
    } finally {
      setRecommendationLoading(false);
    }
  };

  const handleApplyRecommendation = () => {
    if (!recommendation) return;
    setForm((current) => ({ ...current, location_id: String(recommendation.location_id) }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);

    try {
      await createInbound({
        product_id: Number(form.product_id),
        location_id: Number(form.location_id),
        inbound_qty: Number(form.inbound_qty),
      });
      setForm(emptyForm);
      setForecast(null);
      setRecommendation(null);
      await loadInbounds();
      setMessage({ type: "success", text: "입고가 정상적으로 등록되었습니다." });
    } catch (error) {
      console.error(error);
      setMessage({ type: "error", text: error.response?.data?.detail ?? "입고 등록에 실패했습니다." });
    } finally {
      setSubmitting(false);
    }
  };

  const totalInbound = inbounds.reduce((sum, item) => sum + item.inbound_qty, 0);

  return (
    <section className="page-stack">
      <div className="page-intro">
        <div><h2>입고 등록 및 내역</h2><p>도착한 상품을 로케이션별로 빠르게 반영합니다.</p></div>
        <span className="section-tag inbound"><Icon name="inbound" size={16} /> RECEIVING</span>
      </div>

      <div className="operation-layout">
        <article className="form-card">
          <div className="form-card-head">
            <span className="form-card-icon inbound"><Icon name="inbound" /></span>
            <div><h3>새 입고 등록</h3><p>입고 정보를 정확하게 입력해 주세요.</p></div>
          </div>

          <form className="operation-form" onSubmit={handleSubmit}>
            <label className="field"><span>상품 ID</span><input min="1" name="product_id" placeholder="예: 1024" required type="number" value={form.product_id} onChange={handleChange} /></label>
            <label className="field"><span>로케이션 ID</span><input min="1" name="location_id" placeholder="예: 28" required type="number" value={form.location_id} onChange={handleChange} /></label>
            <label className="field"><span>입고 수량</span><div className="input-with-unit"><input min="1" name="inbound_qty" placeholder="0" required type="number" value={form.inbound_qty} onChange={handleChange} /><span>EA</span></div></label>

            <div className="ai-control">
              <button className="secondary-button" disabled={forecastLoading || !form.product_id} type="button" onClick={handleForecastInbound}>
                {forecastLoading ? "AI forecasting..." : "AI qty"}<Icon name="chart" size={18} />
              </button>
              <small>상품 ID 입력 후 예측 가능</small>
            </div>

            <div className="ai-control">
              <button className="secondary-button" disabled={recommendationLoading || !form.product_id || !form.inbound_qty} type="button" onClick={handleRecommendLocation}>
                {recommendationLoading ? "AI checking..." : "AI location"}<Icon name="location" size={18} />
              </button>
              <small>상품 ID와 입고수량 입력 후 추천</small>
            </div>

            {message && <div className={`form-message ${message.type}`} role="status"><Icon name={message.type === "success" ? "check" : "alert"} size={18} />{message.text}</div>}

            <button className="primary-button" disabled={submitting} type="submit">
              {submitting ? "등록 중..." : "입고 등록"}<Icon name="arrow" size={18} />
            </button>
          </form>
        </article>

        <div className="operation-summary inbound-summary">
          <span>누적 입고 수량</span><strong>{totalInbound.toLocaleString()}<small> EA</small></strong>
          <p>현재 조회된 입고 기록 {inbounds.length.toLocaleString()}건의 합계입니다.</p>
          <div className="ai-panel">
            <div>
              <span>AI QTY</span>
              {forecast ? (
                <strong>{forecast.predicted_qty.toLocaleString()}<small>EA</small></strong>
              ) : (
                <strong>--<small>EA</small></strong>
              )}
              <small>{forecast ? `${forecast.target_date} / PRD-${forecast.product_id}` : forecastError ?? "Inbound quantity forecast"}</small>
            </div>
            <div className="ai-actions">
              <button disabled={forecastLoading || !form.product_id} title="Forecast inbound quantity" type="button" onClick={handleForecastInbound}>
                <Icon name="chart" size={15} />
              </button>
              <button disabled={!forecast} title="Apply quantity" type="button" onClick={handleApplyForecast}>
                <Icon name="check" size={15} />
              </button>
            </div>
          </div>
          <div className="ai-panel">
            <div>
              <span>AI LOCATION</span>
              {recommendation ? (
                <strong>LOC-{recommendation.location_id}<small>{recommendation.zone ?? ""}</small></strong>
              ) : (
                <strong>--<small>LOC</small></strong>
              )}
              <small>{recommendation ? `${Math.round(recommendation.confidence * 100)}% / ${recommendation.reason}` : recommendationError ?? "Inbound location recommendation"}</small>
            </div>
            <div className="ai-actions">
              <button disabled={recommendationLoading || !form.product_id || !form.inbound_qty} title="Recommend location" type="button" onClick={handleRecommendLocation}>
                <Icon name="chart" size={15} />
              </button>
              <button disabled={!recommendation} title="Apply location" type="button" onClick={handleApplyRecommendation}>
                <Icon name="check" size={15} />
              </button>
            </div>
          </div>
          <div className="summary-graphic"><Icon name="inbound" size={48} /></div>
        </div>
      </div>

      <OperationTable loading={loading} rows={inbounds} type="inbound" />
    </section>
  );
}

function OperationTable({ loading, rows, type }) {
  return (
    <article className="data-card">
      <div className="card-toolbar"><div><h3>최근 입고 내역</h3><p>최신 등록 순으로 표시됩니다.</p></div><span className="record-count">{rows.length.toLocaleString()} RECORDS</span></div>
      {loading ? <div className="state-message"><Icon name="package" />내역을 불러오는 중입니다.</div> : rows.length === 0 ? <div className="state-message"><Icon name="package" />등록된 입고 내역이 없습니다.</div> : (
        <div className="table-wrap"><table><thead><tr><th>입고 번호</th><th>상품 ID</th><th>로케이션</th><th>입고 수량</th><th>처리 상태</th></tr></thead><tbody>
          {rows.map((item) => <tr key={item.inbound_id}><td className="mono-cell">IN-{String(item.inbound_id).padStart(5, "0")}</td><td><span className="item-id">PRD-{String(item.product_id).padStart(4, "0")}</span></td><td><span className="location-cell"><Icon name="location" size={16} /> LOC-{item.location_id}</span></td><td><strong className="quantity">+{item.inbound_qty.toLocaleString()}</strong><span className="unit"> EA</span></td><td><span className={`status-pill ${type === "inbound" ? "success" : ""}`}>입고 완료</span></td></tr>)}
        </tbody></table></div>
      )}
    </article>
  );
}

export default InboundPage;
