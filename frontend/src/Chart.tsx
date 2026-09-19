import { useEffect, useRef } from "react";
import {
  createChart,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  LineStyle,
} from "lightweight-charts";
import type { Analysis, Pattern } from "./types";
export function Chart({
  data,
  selected,
  visibleSma,
}: {
  data: Analysis;
  selected: Pattern | null;
  visibleSma: { sma75: boolean; sma200: boolean };
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, {
      autoSize: true,
      height: 500,
      layout: { background: { color: "#0B1220" }, textColor: "#E6EDF7" },
      grid: {
        vertLines: { color: "#20314b" },
        horzLines: { color: "#20314b" },
      },
    });
    const candles = chart.addSeries(CandlestickSeries);
    candles.setData(
      data.bars.map((b) => ({
        time: b.date,
        open: b.open,
        high: b.high,
        low: b.low,
        close: b.close,
      })),
    );
    const volume = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });
    chart
      .priceScale("volume")
      .applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });
    volume.setData(
      data.bars.map((b) => ({
        time: b.date,
        value: b.volume ?? 0,
        color: "#5277a8",
      })),
    );
    for (const p of [30, 75, 200]) {
      if (p !== 30 && !visibleSma[`sma${p}` as "sma75" | "sma200"]) continue;
      const line = chart.addSeries(LineSeries, {
        color: p === 30 ? "#4cc9f0" : p === 75 ? "#ffd166" : "#ef476f",
        lineWidth: 2,
      });
      line.setData(
        data.indicators[`sma${p}`]
          .filter((x) => x.value !== null)
          .map((x) => ({ time: x.date, value: x.value! })),
      );
    }
    for (const z of data.zones.slice(0, 7)) {
      for (const value of [z.lower, z.upper]) {
        const line = chart.addSeries(LineSeries, {
          color: z.role === "support" ? "#3a86ff" : "#fb8500",
          lineStyle: LineStyle.Dotted,
          lineWidth: 1,
        });
        line.setData(
          data.bars.length
            ? [
                { time: data.bars[0].date, value },
                { time: data.bars.at(-1)!.date, value },
              ]
            : [],
        );
      }
    }
    if (selected && selected.anchors.length > 1) {
      const line = chart.addSeries(LineSeries, {
        color: "#ffd166",
        lineWidth: 3,
      });
      line.setData(
        selected.anchors.map((a) => ({ time: a.date, value: a.price })),
      );
    }
    chart.timeScale().fitContent();
    const ro = new ResizeObserver(() =>
      chart.resize(
        ref.current!.clientWidth,
        Math.max(320, ref.current!.clientHeight),
      ),
    );
    ro.observe(ref.current);
    return () => {
      ro.disconnect();
      chart.remove();
    };
  }, [data, selected, visibleSma]);
  return (
    <div
      className="chart"
      ref={ref}
      role="img"
      aria-label={`${data.symbol} ローソク足チャート`}
    />
  );
}
