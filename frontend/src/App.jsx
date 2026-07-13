import { NavLink, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import Icon from "./components/Icon";
import HomePage from "./pages/HomePage";
import InboundPage from "./pages/InboundPage";
import InventoryPage from "./pages/InventoryPage";
import LoginPage from "./pages/LoginPage";
import OutboundPage from "./pages/OutboundPage";
import SignupPage from "./pages/SignupPage";
import "./App.css";

const navigation = [
  { to: "/home", label: "홈", icon: "home" },
  { to: "/inventory", label: "재고 현황", icon: "inventory" },
  { to: "/inbound", label: "입고 관리", icon: "inbound" },
  { to: "/outbound", label: "출고 관리", icon: "outbound" },
];

const pageMeta = {
  "/home": { eyebrow: "OVERVIEW", title: "홈" },
  "/inventory": { eyebrow: "WAREHOUSE", title: "재고 현황" },
  "/inbound": { eyebrow: "RECEIVING", title: "입고 관리" },
  "/outbound": { eyebrow: "SHIPPING", title: "출고 관리" },
};

function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const isAuthenticated = Boolean(localStorage.getItem("access_token"));

  if (location.pathname === "/login" || location.pathname === "/signup") {
    if (isAuthenticated) {
      return <Navigate to="/home" replace />;
    }

    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
      </Routes>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  const currentPage = pageMeta[location.pathname] ?? pageMeta["/home"];

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            <Icon name="boxes" />
          </div>
          <div>
            <strong>STOCKFLOW</strong>
            <span>Warehouse OS</span>
          </div>
        </div>

        <div className="sidebar-label">OPERATIONS</div>
        <nav className="sidebar-nav" aria-label="주요 메뉴">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            >
              <Icon name={item.icon} />
              <span>{item.label}</span>
            </NavLink>
          ))}
          <button className="nav-item nav-logout" type="button" onClick={handleLogout}>
            <Icon name="logout" />
            <span>로그아웃</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="system-status">
            <span className="status-dot" />
            <div>
              <strong>시스템 정상</strong>
              <span>API 연결 준비됨</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="topbar-eyebrow">{currentPage.eyebrow}</span>
            <h1>{currentPage.title}</h1>
          </div>
          <div className="operator-chip">
            <span className="operator-avatar">WH</span>
            <div>
              <strong>Warehouse Admin</strong>
              <span>운영 관리자</span>
            </div>
          </div>
        </header>

        <div className="content-area">
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/inventory" element={<InventoryPage />} />
            <Route path="/inbound" element={<InboundPage />} />
            <Route path="/outbound" element={<OutboundPage />} />
            <Route path="*" element={<Navigate to="/home" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
