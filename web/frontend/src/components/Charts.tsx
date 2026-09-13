import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useChartColors } from "../lib/colors";
import type { Stats } from "../lib/api";

const SLOT_LABEL: Record<string, string> = { breakfast: "早餐", lunch: "午餐", dinner: "晚餐" };
const yuan = (n: number) => `¥${n.toFixed(2)}`;

function TooltipBox({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        background: "var(--panel)",
        border: "1px solid var(--border)",
        borderRadius: 8,
        padding: "8px 10px",
        fontSize: 12,
        boxShadow: "var(--shadow-md)",
      }}
    >
      <div style={{ color: "var(--fg-muted)", marginBottom: 2 }}>{label}</div>
      {payload.map((p: any, i: number) => (
        <div key={i} className="mono" style={{ color: "var(--fg)" }}>
          {yuan(p.value)}
        </div>
      ))}
    </div>
  );
}

export function DailyTrendChart({ data }: { data: NonNullable<Stats["daily_series"]> }) {
  const c = useChartColors();
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="fillDaily" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={c.accent} stopOpacity={0.28} />
            <stop offset="100%" stopColor={c.accent} stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date"
          tick={{ fill: c.axis, fontSize: 11 }}
          tickLine={false}
          axisLine={{ stroke: c.grid }}
          minTickGap={48}
          tickFormatter={(d) => d.slice(5)}
        />
        <YAxis
          tick={{ fill: c.axis, fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          width={40}
          tickFormatter={(v) => `${v}`}
        />
        <Tooltip content={<TooltipBox />} />
        <Area
          type="monotone"
          dataKey="amount"
          stroke={c.accent}
          strokeWidth={2}
          fill="url(#fillDaily)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function MonthlyBarChart({ data }: { data: NonNullable<Stats["by_month"]> }) {
  const c = useChartColors();
  const rows = data.map((d) => ({ label: `${d.month}月`, amount: d.sum }));
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={rows} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <XAxis dataKey="label" tick={{ fill: c.axis, fontSize: 11 }} tickLine={false} axisLine={{ stroke: c.grid }} />
        <YAxis tick={{ fill: c.axis, fontSize: 11 }} tickLine={false} axisLine={false} width={40} />
        <Tooltip content={<TooltipBox />} cursor={{ fill: "var(--panel-hover)" }} />
        <Bar dataKey="amount" fill={c.accent} radius={[4, 4, 0, 0]} maxBarSize={40} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function TypeDonut({ data }: { data: NonNullable<Stats["by_type"]> }) {
  const c = useChartColors();
  const rows = data.map((d) => ({ name: d.type || "其他", value: d.sum }));
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie data={rows} dataKey="value" nameKey="name" innerRadius={58} outerRadius={90} paddingAngle={2} stroke="none">
          {rows.map((_, i) => (
            <Cell key={i} fill={c.categorical[i % c.categorical.length]} />
          ))}
        </Pie>
        <Tooltip content={<TooltipBox />} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function TimeSlotBars({ data }: { data: NonNullable<Stats["by_time_slot"]> }) {
  const c = useChartColors();
  const rows = data.map((d) => ({ label: SLOT_LABEL[d.slot] ?? d.slot, amount: d.sum, slot: d.slot }));
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 12, bottom: 4, left: 8 }}>
        <XAxis type="number" tick={{ fill: c.axis, fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="label" tick={{ fill: c.text, fontSize: 12 }} tickLine={false} axisLine={false} width={44} />
        <Tooltip content={<TooltipBox />} cursor={{ fill: "var(--panel-hover)" }} />
        <Bar dataKey="amount" radius={[0, 4, 4, 0]} maxBarSize={28}>
          {rows.map((r, i) => (
            <Cell key={i} fill={c.slots[r.slot] ?? c.accent} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
