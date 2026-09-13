import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type CardRecord, type Stats, type UserInfo } from "../lib/api";
import { Button, Card, Spinner, ThemeToggle } from "../components/ui";
import { StatTiles } from "../components/StatTiles";
import { RecordsTable } from "../components/RecordsTable";
import { DailyTrendChart, MonthlyBarChart, TimeSlotBars, TypeDonut } from "../components/Charts";

const now = new Date();
const DEFAULT_YEAR = String(now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear());
const YEARS = Array.from({ length: 6 }, (_, i) => String(Number(DEFAULT_YEAR) - i));

const EXTREME_LABELS: Record<string, string> = {
  max: "最大单笔",
  max_dining: "最大食堂单笔",
  min: "最小单笔",
  earliest: "年度首笔",
  latest: "年度末笔",
  earliest_of_day: "每日最早",
  latest_of_day: "每日最晚",
};

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h2 style={{ fontSize: 15, margin: "4px 0 2px" }}>{children}</h2>;
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card>
      <div className="card-head">
        <div className="card-title">{title}</div>
      </div>
      <div className="card-pad">{children}</div>
    </Card>
  );
}

export function Dashboard({ user, onLogout }: { user: UserInfo; onLogout: () => void }) {
  const [year, setYear] = useState(DEFAULT_YEAR);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [records, setRecords] = useState<CardRecord[]>([]);

  const load = useCallback(async (y: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.records(y);
      setStats(res.stats);
      setRecords(res.records);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "加载数据失败");
      setStats(null);
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(year);
  }, [year, load]);

  const extremes = stats?.extremes ?? {};

  return (
    <div>
      <header className="topbar">
        <div className="container topbar-inner">
          <div className="brand">
            <span className="brand-mark">T</span>
            <span>TJU Expense</span>
          </div>
          <div className="grow" />
          <div className="tabs" role="tablist" aria-label="年份">
            {YEARS.map((y) => (
              <button key={y} className="tab" data-active={y === year} onClick={() => setYear(y)}>
                {y}
              </button>
            ))}
          </div>
          <ThemeToggle />
          <Button variant="ghost" className="btn-sm" onClick={onLogout}>
            退出
          </Button>
        </div>
      </header>

      <main className="container" style={{ paddingBlock: 24 }}>
        <div className="row" style={{ justifyContent: "space-between", marginBottom: 18, flexWrap: "wrap", gap: 8 }}>
          <div>
            <h1 style={{ fontSize: 22 }}>你好，{user.name}</h1>
            <p className="muted small" style={{ margin: "4px 0 0" }}>
              {user.stuid && <span className="mono">{user.stuid}</span>}
              {user.balance && <span> · 校园卡余额 <strong style={{ color: "var(--money)" }}>¥{user.balance}</strong></span>}
            </p>
          </div>
        </div>

        {loading && (
          <div className="row muted" style={{ gap: 10, padding: "60px 0", justifyContent: "center" }}>
            <Spinner /> 正在获取 {year} 年数据…
          </div>
        )}

        {!loading && error && <div className="alert alert-error">{error}</div>}

        {!loading && stats && stats.empty && (
          <div className="alert alert-info">{year} 年暂无消费数据。</div>
        )}

        {!loading && stats && !stats.empty && (
          <div className="stack" style={{ gap: 24 }}>
            <StatTiles stats={stats} />

            <ChartCard title="每日消费趋势">
              <DailyTrendChart data={stats.daily_series!} />
            </ChartCard>

            <div className="grid-2">
              <ChartCard title="每月消费">
                <MonthlyBarChart data={stats.by_month!} />
              </ChartCard>
              <ChartCard title="消费类型占比">
                <TypeDonut data={stats.by_type!} />
              </ChartCard>
            </div>

            <ChartCard title="三餐时段消费">
              <TimeSlotBars data={stats.by_time_slot!} />
            </ChartCard>

            <div>
              <SectionTitle>消费之最</SectionTitle>
              <div className="stat-grid" style={{ marginTop: 12 }}>
                {Object.entries(EXTREME_LABELS)
                  .filter(([k]) => extremes[k])
                  .map(([k, label]) => {
                    const t = extremes[k];
                    return (
                      <div className="stat" key={k}>
                        <div className="stat-label">{label}</div>
                        <div className="stat-value" style={{ fontSize: 20, color: "var(--money)" }}>
                          ¥{t.amount.toFixed(2)}
                        </div>
                        <div className="stat-sub">{t.place || "—"}</div>
                        <div className="faint small mono" style={{ marginTop: 2 }}>{t.time}</div>
                      </div>
                    );
                  })}
              </div>
            </div>

            {stats.top_places && stats.top_places.length > 0 && (
              <Card>
                <div className="card-head">
                  <div className="card-title">常去地点 Top 10</div>
                </div>
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>地点</th>
                        <th style={{ textAlign: "right" }}>笔数</th>
                        <th style={{ textAlign: "right" }}>合计</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.top_places.map((p, i) => (
                        <tr key={i}>
                          <td>{p.place || "—"}</td>
                          <td className="num">{p.count}</td>
                          <td className="num" style={{ color: "var(--money)" }}>¥{p.sum.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}

            <Card>
              <RecordsTable records={records} />
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
