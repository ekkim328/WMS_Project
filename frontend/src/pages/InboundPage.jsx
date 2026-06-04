import { useEffect, useState } from "react";
import { createInbound, getInbounds } from "../api/inbound";

function InboundPage() {
  const [inbounds, setInbounds] = useState([]);
  const [form, setForm] = useState({
    product_id: "",
    location_id: "",
    inbound_qty: "",
  });

  const loadInbounds = async () => {
    const data = await getInbounds();
    setInbounds(data);
  };

  useEffect(() => {
    loadInbounds();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await createInbound({
      product_id: Number(form.product_id),
      location_id: Number(form.location_id),
      inbound_qty: Number(form.inbound_qty),
    });

    setForm({ product_id: "", location_id: "", inbound_qty: "" });
    loadInbounds();
  };

  return (
    <div>
      <h2>입고 관리</h2>

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
          name="inbound_qty"
          placeholder="입고 수량"
          value={form.inbound_qty}
          onChange={handleChange}
        />
        <button type="submit">입고 등록</button>
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
          {inbounds.map((item) => (
            <tr key={item.inbound_id}>
              <td>{item.inbound_id}</td>
              <td>{item.product_id}</td>
              <td>{item.location_id}</td>
              <td>{item.inbound_qty}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default InboundPage;
