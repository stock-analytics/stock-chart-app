export type Bar = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
};
export type Pattern = {
  id: string;
  type: string;
  direction: "bullish" | "bearish" | "neutral";
  state: string;
  reaction_state: string;
  anchors: { label: string; date: string; price: number; known_at: string }[];
  checks: { name: string; actual: number; passed: boolean }[];
  rule_version: string;
};
export type Analysis = {
  symbol: string;
  timeframe?: string;
  data_mode: string;
  snapshot_id: string;
  metadata: {
    latest_final_session: string | null;
    fetched_at: string | null;
    price_basis: string;
    warnings: string[];
  };
  bars: Bar[];
  provisional_bars: Bar[];
  indicators: Record<string, { date: string; value: number | null }[]>;
  zones: { lower: number; upper: number; role: string; touches: number }[];
  patterns: Pattern[];
  insufficient_data_reasons: string[];
};
