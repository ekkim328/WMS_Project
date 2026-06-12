import { useEffect, useState } from "react";

import { createOutbound, getOutbounds } from "../api/outbound";
import Icon from "../components/Icon";

const emptyForm = { product_id: "", location_id: "", outbound_qty: "" };

function OutboundPage() {
  const [outbounds, setOutbounds] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  const loadOutbounds = async () => {
    const data = await getOutbounds();
    setOutbounds(data);
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

    return () => { active = false; };
  }, []);

  const handleChange = (event) => {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
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
            <label className="field"><span>상품 ID</span><input min="1" name="product_id" placeholder="예: 1024" required type="number" value={form.product_id} onChange={handleChange} /></label>
            <label className="field"><span>로케이션 ID</span><input min="1" name="location_id" placeholder="예: 28" required type="number" value={form.location_id} onChange={handleChange} /></label>
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
    </section>
  );
}

export default OutboundPage;
