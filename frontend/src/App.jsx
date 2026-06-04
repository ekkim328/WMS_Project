import { useState } from "react";
import InboundPage from "./pages/InboundPage";
import InventoryPage from "./pages/InventoryPage";
import OutboundPage from "./pages/OutboundPage";

function App() {
  const [page, setPage] = useState("inventory");

  return (
    <div>
      <h1>WMS 관리 시스템</h1>

      <nav>
        <button onClick={() => setPage("inventory")}>재고 조회</button>
        <button onClick={() => setPage("inbound")}>입고 관리</button>
        <button onClick={() => setPage("outbound")}>출고 관리</button>
      </nav>

      {page === "inventory" && <InventoryPage />}
      {page === "inbound" && <InboundPage />}
      {page === "outbound" && <OutboundPage />}
    </div>
  );
}

export default App;