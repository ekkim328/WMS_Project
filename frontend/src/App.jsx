import { Link, Navigate, Route, Routes } from "react-router-dom";

import InboundPage from "./pages/InboundPage";
import InventoryPage from "./pages/InventoryPage";
import LoginPage from "./pages/LoginPage";
import OutboundPage from "./pages/OutboundPage";

function App() {
  return (
    <div>
      <h1>WMS 관리 시스템</h1>

      <nav>
        <Link to="/login">로그인</Link> | <Link to="/inventory">재고 조회</Link>{" "}
        | <Link to="/inbound">입고 관리</Link> |{" "}
        <Link to="/outbound">출고 관리</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/inbound" element={<InboundPage />} />
        <Route path="/outbound" element={<OutboundPage />} />
      </Routes>
    </div>
  );
}

export default App;
