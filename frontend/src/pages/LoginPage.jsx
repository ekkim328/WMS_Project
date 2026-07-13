import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { login } from "../api/auth";
import Icon from "../components/Icon";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await login(username, password);
      const destination = location.state?.from;
      navigate(destination && destination !== "/login" ? destination : "/home", {
        replace: true,
      });
    } catch (requestError) {
      console.error(requestError);
      setError("아이디 또는 비밀번호를 다시 확인해 주세요.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-visual">
        <div className="login-brand">
          <span className="brand-mark"><Icon name="boxes" size={24} /></span>
          <strong>STOCKFLOW</strong>
        </div>
        <div className="login-copy">
          <span className="eyebrow-light">WAREHOUSE MANAGEMENT SYSTEM</span>
          <h1>창고 운영의 흐름을<br />한눈에 관리하세요.</h1>
          <p>입고부터 재고, 출고까지 연결된 운영 데이터를 빠르고 정확하게 확인합니다.</p>
        </div>
        <div className="login-metrics">
          <div><strong>01</strong><span>실시간 재고 현황</span></div>
          <div><strong>02</strong><span>안전한 입출고 처리</span></div>
          <div><strong>03</strong><span>명확한 작업 이력</span></div>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <span className="section-kicker">WELCOME BACK</span>
          <h2>운영자 로그인</h2>
          <p className="muted-copy">계정 정보를 입력해 관리 시스템에 접속하세요.</p>

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>아이디</span>
              <input
                autoComplete="username"
                placeholder="아이디를 입력하세요"
                required
                value={username}
                onChange={(event) => setUsername(event.target.value)}
              />
            </label>

            <label className="field">
              <span>비밀번호</span>
              <input
                autoComplete="current-password"
                type="password"
                placeholder="비밀번호를 입력하세요"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>

            {error && (
              <div className="form-message error" role="alert">
                <Icon name="alert" size={18} />
                {error}
              </div>
            )}

            <button className="primary-button login-submit" disabled={submitting} type="submit">
              {submitting ? "접속 중..." : "관리 시스템 접속"}
              {!submitting && <Icon name="arrow" size={18} />}
            </button>
          </form>

          <p className="auth-switch">
            아직 계정이 없으신가요? <Link to="/signup">회원가입</Link>
          </p>
          <p className="login-help">접속에 문제가 있다면 시스템 관리자에게 문의하세요.</p>
        </div>
      </section>
    </main>
  );
}

export default LoginPage;
