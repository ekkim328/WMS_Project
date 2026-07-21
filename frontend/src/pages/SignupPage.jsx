import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { login, signup } from "../api/auth";
import Icon from "../components/Icon";

const passwordByteLength = (value) => new TextEncoder().encode(value).length;

const getRequestErrorMessage = (error) => {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") {
    if (detail.includes("사용자 이름")) {
      return "이미 사용 중인 아이디입니다.";
    }

    return detail;
  }

  return "회원가입에 실패했습니다. 입력 정보를 확인한 뒤 다시 시도해 주세요.";
};

function SignupPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    name: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    const username = form.username.trim();
    const name = form.name.trim();

    if (!username) {
      setError("아이디를 입력해 주세요.");
      return;
    }

    if (!name) {
      setError("이름을 입력해 주세요.");
      return;
    }

    if (form.password.length < 4) {
      setError("비밀번호는 4자 이상이어야 합니다.");
      return;
    }

    if (passwordByteLength(form.password) > 72) {
      setError("비밀번호는 72바이트 이내로 입력해 주세요.");
      return;
    }

    setSubmitting(true);

    try {
      await signup({ username, name, password: form.password });
      await login(username, form.password);
      navigate("/home", { replace: true });
    } catch (requestError) {
      console.error(requestError);
      setError(getRequestErrorMessage(requestError));
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
          <span className="eyebrow-light">JOIN THE OPERATION</span>
          <h1>새로운 운영 계정을<br />간편하게 시작하세요.</h1>
          <p>하나의 계정으로 입고, 재고, 출고 흐름을 확인하고 창고 운영을 이어갈 수 있습니다.</p>
        </div>
        <div className="login-metrics">
          <div><strong>01</strong><span>간편한 계정 생성</span></div>
          <div><strong>02</strong><span>안전한 비밀번호 보호</span></div>
          <div><strong>03</strong><span>가입 즉시 시스템 접속</span></div>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-card signup-card">
          <span className="section-kicker">CREATE ACCOUNT</span>
          <h2>회원가입</h2>
          <p className="muted-copy">창고 관리 시스템에서 사용할 계정을 만들어 주세요.</p>

          <form className="login-form signup-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>아이디</span>
              <input
                autoComplete="username"
                maxLength={40}
                name="username"
                placeholder="사용할 아이디를 입력하세요"
                required
                value={form.username}
                onChange={handleChange}
              />
            </label>

            <label className="field">
              <span>이름</span>
              <input
                autoComplete="name"
                maxLength={100}
                name="name"
                placeholder="이름을 입력하세요"
                required
                value={form.name}
                onChange={handleChange}
              />
            </label>

            <label className="field">
              <span>비밀번호</span>
              <input
                autoComplete="new-password"
                minLength={4}
                name="password"
                placeholder="4자 이상 입력하세요"
                required
                type="password"
                value={form.password}
                onChange={handleChange}
              />
            </label>

            {error && (
              <div className="form-message error" role="alert">
                <Icon name="alert" size={18} />
                {error}
              </div>
            )}

            <button className="primary-button login-submit" disabled={submitting} type="submit">
              {submitting ? "계정 생성 중..." : "계정 만들기"}
              {!submitting && <Icon name="arrow" size={18} />}
            </button>
          </form>

          <p className="auth-switch">
            이미 계정이 있으신가요? <Link to="/login">로그인</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default SignupPage;
