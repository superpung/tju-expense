import type { Stats } from "../lib/api";

function Tile({ label, value, unit, sub }: { label: string; value: string; unit?: string; sub?: string }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value">
        {value}
        {unit && <span className="unit">{unit}</span>}
      </div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

export function StatTiles({ stats }: { stats: Stats }) {
  const s = stats.summary!;
  return (
    <div className="stat-grid">
      <Tile label="年度总消费" value={`¥${s.total.toFixed(2)}`} sub={`${s.first_day} — ${s.last_day}`} />
      <Tile label="消费笔数" value={`${s.count}`} unit="笔" sub={`覆盖 ${s.active_days} 天`} />
      <Tile label="日均消费" value={`¥${s.daily_average.toFixed(2)}`} sub="有消费当日平均" />
      <Tile label="单笔均值" value={`¥${s.per_transaction_average.toFixed(2)}`} sub="每笔平均金额" />
    </div>
  );
}
