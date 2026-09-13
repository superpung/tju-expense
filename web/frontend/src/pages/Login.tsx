import { useState } from "react";
import { api, ApiError, type UserInfo } from "../lib/api";
import { Button, Card, Field, Input, ThemeToggle } from "../components/ui";

export function Login({ onSuccess }: { onSuccess: (user: UserInfo) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const user = await api.login(username.trim(), password);
      onSuccess(user);
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.message
          : "无法连接服务，请确认后端已启动且处于校园网环境。",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="center-screen">
      <div style={{ position: "fixed", top: 16, right: 16 }}>
        <ThemeToggle />
      </div>
      <Card className="login-card card-pad">
        <div className="stack" style={{ gap: 6, marginBottom: 20 }}>
          <div className="brand">
            <span className="brand-mark">T</span>
            <span>TJU Expense</span>
          </div>
          <p className="muted small" style={{ margin: 0 }}>
            登录天津大学校园卡，查看消费流水与统计。
          </p>
        </div>

        <form className="stack" style={{ gap: 14 }} onSubmit={submit}>
          <Field label="学工号">
            <Input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              placeholder="学号 / 工号"
              required
              autoFocus
            />
          </Field>
          <Field label="密码">
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              placeholder="校园卡查询密码"
              required
            />
          </Field>

          {error && <div className="alert alert-error">{error}</div>}

          <Button type="submit" variant="primary" className="btn-block" loading={submitting}>
            登录
          </Button>
        </form>

        <p className="faint small" style={{ marginTop: 16, marginBottom: 0 }}>
          账号密码仅用于向校园卡系统登录，服务端不会存储。
        </p>
      </Card>
    </div>
  );
}
