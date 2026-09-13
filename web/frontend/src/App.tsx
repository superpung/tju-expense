import { useState } from "react";
import { api, type UserInfo } from "./lib/api";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";

export function App() {
  const [user, setUser] = useState<UserInfo | null>(null);

  const logout = async () => {
    await api.logout();
    setUser(null);
  };

  if (!user) return <Login onSuccess={setUser} />;
  return <Dashboard user={user} onLogout={logout} />;
}
