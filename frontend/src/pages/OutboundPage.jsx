import { useEffect, useState } from "react";
import { createOutbound, getOutbounds } from "../api/outbound";

function OutboundPage() {
  const [outbounds, setOutbounds] = useState([]);
  const [form, setForm] = useState({
    product_id: "",
    location_id: "",
    outbound_qty: "",
  });

  const loadOutbounds = async () => {
    const data = await getOutbounds();
    setOutbounds(data);
  };

  useEffect(() => {
    loadOutbounds();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await createOutbound({
      product_id: Number(form.product_id),
      location_id: Number(form.location_id),
      inbound_qty: Number(form.outbound_qty),
    });

    setForm({ product_id: "", location_id: "", outbound_qty: "" });
    loadOutbounds();
  };

  return (
    <div>
      <h2>출고 관리</h2>

      <form onSubmit={handleSubmit}>
        <input
          name="product_id"
          placeholder="상품 ID"
          value={form.product_id}
          onChange={handleChange}
        />
        <input
          name="location_id"
          placeholder="로케이션 ID"
          value={form.location_id}
          onChange={handleChange}
        />
        <input
          name="outbound_qty"
          placeholder="출고 수량"
          value={form.outbound_qty}
          onChange={handleChange}
        />
        <button type="submit">출고 등록</button>
      </form>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>상품ID</th>
            <th>로케이션ID</th>
            <th>수량</th>
          </tr>
        </thead>
        <tbody>
          {outbounds.map((item) => (
            <tr key={item.outbound_id}>
              <td>{item.outbound_id}</td>
              <td>{item.product_id}</td>
              <td>{item.location_id}</td>
              <td>{item.outbound_qty}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default OutboundPage;
