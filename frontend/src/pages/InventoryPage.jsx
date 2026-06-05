import { useEffect, useState } from "react";
import { getInventories } from "../api/inventory";

function InventoryPage() {
  const [inventories, setInventories] = useState([]);

  useEffect(() => {
    const load = async () => {
      const data = await getInventories();
      setInventories(data);
    };

    load();
  }, []);

  return (
    <div>
      <h2>재고 조회</h2>

      <table>
        <thead>
          <tr>
            <th>재고 ID</th>
            <th>상품 ID</th>
            <th>로케이션 ID</th>
            <th>현재 재고</th>
          </tr>
        </thead>
        <tbody>
          {inventories.map((item) => (
            <tr key={item.inventory_id}>
              <td>{item.inventory_id}</td>
              <td>{item.product_id}</td>
              <td>{item.location_id}</td>
              <td>{item.stock_qty}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default InventoryPage;
