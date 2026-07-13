import { useEffect, useMemo, useState } from "react";

import { getInbounds } from "../api/inbound";
import { getOutbounds } from "../api/outbound";
import Icon from "../components/Icon";

const DAYS_TO_SHOW = 14;
const CHART = { width: 1000, height: 360, left: 68, right: 24, top: 28, bottom: 52 };

const toDateKey = (value) => String(value ?? "").slice(0, 10);

const shiftDateKey = (dateKey, amount) => {
  const [year, month, day] = dateKey.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day + amount));
  return date.toISOString().slice(0, 10);
};

const formatShortDate = (dateKey) => {
  const [, month, day] = dateKey.split("-");
  return `${Number(month)}/${Number(day)}`;
};

const formatRangeDate = (dateKey) => dateKey.replaceAll("-", ".");

const makeNiceMaximum = (value) => {
  if (value <= 0) return 100;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const normalized = value / magnitude;
  const nice = normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10;
  return nice * magnitude;
};

function DailyFlowChart({ rows }) {
  const plotWidth = CHART.width - CHART.left - CHART.right;
  const plotHeight = CHART.height - CHART.top - CHART.bottom;
  const maximum = makeNiceMaximum(
    Math.max(...rows.flatMap((row) => [row.inbound, row.outbound]), 0),
  );
  const x = (index) => CHART.left + (plotWidth * index) / Math.max(rows.length - 1, 1);
  const y = (value) => CHART.top + plotHeight - (value / maximum) * plotHeight;
  const points = (key) => rows.map((row, index) => `${x(index)},${y(row[key])}`).join(" ");
  const gridValues = Array.from({ length: 5 }, (_, index) => (maximum * index) / 4);

  return (
    <div className="flow-chart-scroll">
      <svg
        aria-label="최근 14일의 일자별 입고 수량과 출고 수량 꺾은선 그래프"
        className="flow-chart"
        role="img"
        viewBox={`0 0 ${CHART.width} ${CHART.height}`}
      >
        {gridValues.map((value) => (
          <g key={value}>
            <line
              className="chart-grid-line"
              x1={CHART.left}
              x2={CHART.width - CHART.right}
              y1={y(value)}
              y2={y(value)}
            />
            <text className="chart-axis-label" textAnchor="end" x={CHART.left - 13} y={y(value) + 4}>
              {Math.round(value).toLocaleString()}
            </text>
          </g>
        ))}

        {rows.map((row, index) => (
          <text
            className="chart-axis-label"
            key={row.date}
            textAnchor="middle"
            x={x(index)}
            y={CHART.height - 18}
          >
            {index % 2 === 0 || index === rows.length - 1 ? formatShortDate(row.date) : ""}
          </text>
        ))}

        <polyline className="chart-line inbound-line" points={points("inbound")} />
        <polyline className="chart-line outbound-line" points={points("outbound")} />

        {rows.map((row, index) => (
          <g key={`points-${row.date}`}>
            <circle className="chart-point inbound-point" cx={x(index)} cy={y(row.inbound)} r="4.5">
              <title>{`${row.date} 입고 ${row.inbound.toLocaleString()} EA`}</title>
            </circle>
            <circle className="chart-point outbound-point" cx={x(index)} cy={y(row.outbound)} r="4.5">
              <title>{`${row.date} 출고 ${row.outbound.toLocaleString()} EA`}</title>
            </circle>
          </g>
        ))}
      </svg>
    </div>
  );
}

function HomePage() {
  const [inbounds, setInbounds] = useState([]);
  const [outbounds, setOutbounds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    Promise.all([getInbounds(), getOutbounds()])
      .then(([inboundData, outboundData]) => {
        if (!active) return;
        setInbounds(inboundData);
        setOutbounds(outboundData);
      })
      .catch((requestError) => {
        console.error(requestError);
        if (active) setError("입출고 현황을 불러오지 못했습니다.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const dailyRows = useMemo(() => {
    const datedRecords = [
      ...inbounds.map((item) => toDateKey(item.inbound_date)),
      ...outbounds.map((item) => toDateKey(item.outbound_date)),
    ].filter(Boolean);
    const latestDate = datedRecords.sort().at(-1) ?? new Date().toISOString().slice(0, 10);
    const firstDate = shiftDateKey(latestDate, -(DAYS_TO_SHOW - 1));
    const rows = Array.from({ length: DAYS_TO_SHOW }, (_, index) => ({
      date: shiftDateKey(firstDate, index),
      inbound: 0,
      outbound: 0,
    }));
    const rowsByDate = new Map(rows.map((row) => [row.date, row]));

    inbounds.forEach((item) => {
      const row = rowsByDate.get(toDateKey(item.inbound_date));
      if (row) row.inbound += Number(item.inbound_qty) || 0;
    });
    outbounds.forEach((item) => {
      const row = rowsByDate.get(toDateKey(item.outbound_date));
      if (row) row.outbound += Number(item.outbound_qty) || 0;
    });

    return rows;
  }, [inbounds, outbounds]);

  const periodInbound = dailyRows.reduce((sum, row) => sum + row.inbound, 0);
  const periodOutbound = dailyRows.reduce((sum, row) => sum + row.outbound, 0);
  const periodNet = periodInbound - periodOutbound;
  const hasData = inbounds.length > 0 || outbounds.length > 0;

  return (
    <section className="page-stack">
      <div className="page-intro">
        <div>
          <h2>입출고 현황</h2>
          <p>일자별 입고량과 출고량의 흐름을 한눈에 확인합니다.</p>
        </div>
        <span className="sync-badge"><span className="status-dot" /> LIVE DATA</span>
      </div>

      <div className="home-metric-grid">
        <article className="home-metric inbound-metric">
          <span className="home-metric-icon"><Icon name="inbound" /></span>
          <div><span>기간 입고량</span><strong>{periodInbound.toLocaleString()} <small>EA</small></strong></div>
        </article>
        <article className="home-metric outbound-metric">
          <span className="home-metric-icon"><Icon name="outbound" /></span>
          <div><span>기간 출고량</span><strong>{periodOutbound.toLocaleString()} <small>EA</small></strong></div>
        </article>
        <article className="home-metric net-metric">
          <span className="home-metric-icon"><Icon name="chart" /></span>
          <div><span>기간 순증감</span><strong>{periodNet > 0 ? "+" : ""}{periodNet.toLocaleString()} <small>EA</small></strong></div>
        </article>
      </div>

      <article className="data-card flow-chart-card">
        <div className="card-toolbar chart-toolbar">
          <div>
            <h3>일자별 입출고 추이</h3>
            <p>{formatRangeDate(dailyRows[0].date)} — {formatRangeDate(dailyRows.at(-1).date)}</p>
          </div>
          <div className="chart-legend" aria-label="그래프 범례">
            <span><i className="legend-dot inbound-dot" />입고</span>
            <span><i className="legend-dot outbound-dot" />출고</span>
          </div>
        </div>

        {loading ? (
          <div className="state-message"><Icon name="chart" />현황을 불러오는 중입니다.</div>
        ) : error ? (
          <div className="state-message error"><Icon name="alert" />{error}</div>
        ) : !hasData ? (
          <div className="state-message"><Icon name="chart" />표시할 입출고 기록이 없습니다.</div>
        ) : (
          <DailyFlowChart rows={dailyRows} />
        )}
      </article>
    </section>
  );
}

export default HomePage;
