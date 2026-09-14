import { useMemo, useState } from "react";
import type { CardRecord } from "../lib/api";
import { Input } from "./ui";

const PAGE = 20;

export function RecordsTable({ records }: { records: CardRecord[] }) {
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    const q = query.trim();
    if (!q) return records;
    return records.filter(
      (r) => (r.place ?? "").includes(q) || (r.type ?? "").includes(q),
    );
  }, [records, query]);

  const pages = Math.max(1, Math.ceil(filtered.length / PAGE));
  const current = Math.min(page, pages - 1);
  const slice = filtered.slice(current * PAGE, current * PAGE + PAGE);

  return (
    <div>
      <div className="card-head">
        <div className="card-title">消费明细</div>
        <div style={{ width: 200 }}>
          <Input
            className="input"
            placeholder="搜索地点 / 类型"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setPage(0);
            }}
          />
        </div>
      </div>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>时间</th>
              <th>类型</th>
              <th>地点</th>
              <th style={{ textAlign: "right" }}>金额</th>
            </tr>
          </thead>
          <tbody>
            {slice.map((r, i) => {
              const amt = Number(r.amount);
              return (
                <tr key={`${r.id ?? ""}-${i}`}>
                  <td className="mono" style={{ whiteSpace: "nowrap", color: "var(--fg-secondary)" }}>{r.time}</td>
                  <td>{r.type || "—"}</td>
                  <td>{r.place || "—"}</td>
                  <td
                    className="num"
                    style={{ color: amt < 0 ? "var(--success)" : "var(--money)", fontWeight: 500 }}
                  >
                    {amt < 0 ? "" : "¥"}
                    {amt.toFixed(2)}
                  </td>
                </tr>
              );
            })}
            {slice.length === 0 && (
              <tr>
                <td colSpan={4} className="muted" style={{ textAlign: "center", padding: 28 }}>
                  没有匹配的记录
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {pages > 1 && (
        <div className="row" style={{ justifyContent: "space-between", padding: "12px 20px" }}>
          <span className="faint small">
            {filtered.length} 条 · 第 {current + 1}/{pages} 页
          </span>
          <div className="row" style={{ gap: 8 }}>
            <button className="btn btn-sm" disabled={current === 0} onClick={() => setPage(current - 1)}>
              上一页
            </button>
            <button className="btn btn-sm" disabled={current >= pages - 1} onClick={() => setPage(current + 1)}>
              下一页
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
