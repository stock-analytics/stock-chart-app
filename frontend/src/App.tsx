import { FormEvent, useEffect, useRef, useState } from "react";
import { Chart } from "./Chart";
import type { Analysis, Pattern } from "./types";
import "./style.css";
const labels: Record<string, string> = {
  double_bottom: "ダブルボトム",
  double_top: "ダブルトップ",
  triple_bottom: "トリプルボトム",
  triple_top: "トリプルトップ",
  head_shoulders: "三尊",
  inverse_head_shoulders: "逆三尊",
  ascending_triangle: "上昇型三角",
  descending_triangle: "下降型三角",
  symmetrical_triangle: "対称三角",
  rising_wedge: "上昇ウェッジ",
  falling_wedge: "下降ウェッジ",
  bull_flag: "強気フラッグ",
  bear_flag: "弱気フラッグ",
  bull_pennant: "強気ペナント",
  bear_pennant: "弱気ペナント",
  cup_handle: "カップ・ウィズ・ハンドル",
  crab: "クラブ",
  deep_crab: "ディープクラブ",
  gartley: "ガートレー",
  bat: "バット",
  butterfly: "バタフライ",
};
let csrf = "";
async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  if (init.method && init.method !== "GET" && csrf)
    headers.set("x-csrf-token", csrf);
  return fetch(path, { ...init, headers });
}
export default function App() {
  const [symbol, setSymbol] = useState("DEMO_7203"),
    [tf, setTf] = useState("1d"),
    [range, setRange] = useState("2y");
  const [data, setData] = useState<Analysis | null>(null),
    [selected, setSelected] = useState<Pattern | null>(null),
    [status, setStatus] = useState("");
  const [watch, setWatch] = useState<string[]>([]),
    [panel, setPanel] = useState<"settings" | "about" | null>(null),
    [sma, setSma] = useState({ sma75: false, sma200: false });
  const request = useRef(0);
  async function load(e?: FormEvent) {
    e?.preventDefault();
    const id = ++request.current;
    setStatus("読み込み中");
    try {
      let r = await api("/api/analyze", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ symbol, timeframe: tf, range }),
      });
      if (r.status === 202) {
        const j = await r.json();
        for (let i = 0; i < 30; i++) {
          await new Promise((x) => setTimeout(x, 100));
          const q = await api(`/api/jobs/${j.job_id}`).then((x) => x.json());
          if (q.status === "succeeded") break;
          if (q.status === "failed") throw Error(q.error);
        }
        r = await api("/api/analyze", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ symbol, timeframe: tf, range }),
        });
      }
      if (!r.ok) throw Error((await r.text()) || "provider_error");
      const d = await r.json();
      if (id === request.current) {
        setData(d);
        setStatus("");
      }
    } catch (x) {
      if (id === request.current)
        setStatus(
          `データ取得エラー: ${x instanceof Error ? x.message : String(x)}`,
        );
    }
  }
  async function favorite() {
    const r = await api("/api/watchlist", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ symbol }),
    });
    if (r.ok) setWatch(await r.json());
  }
  async function saveSettings(next: typeof sma) {
    setSma(next);
    await api("/api/settings", {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(next),
    });
  }
  async function removeLocal() {
    if (!confirm("ローカルの株価・履歴・設定を削除しますか？")) return;
    await api("/api/local-data", {
      method: "DELETE",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ confirmation: "DELETE" }),
    });
    setData(null);
    setWatch([]);
    setPanel(null);
  }
  useEffect(() => {
    load();
  }, [tf, range]);
  useEffect(() => {
    api("/api/watchlist")
      .then((r) => (r.ok ? r.json() : []))
      .then(setWatch);
    api("/api/settings")
      .then((r) => (r.ok ? r.json() : {}))
      .then((x) => setSma({ sma75: !!x.sma75, sma200: !!x.sma200 }));
    if ("serviceWorker" in navigator)
      navigator.serviceWorker.register("/sw.js");
  }, []);
  return (
    <>
      <header>
        <h1>Chart Lens</h1>
        <form onSubmit={load}>
          <label>
            銘柄コード
            <input
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              aria-label="銘柄コード"
            />
          </label>
          <button>分析</button>
          <button type="button" onClick={favorite}>
            お気に入り
          </button>
        </form>
        <nav aria-label="アプリメニュー">
          <button onClick={() => setPanel("settings")}>設定</button>
          <button onClick={() => setPanel("about")}>データとライセンス</button>
        </nav>
        <div className="filters">
          <label>
            足種
            <select value={tf} onChange={(e) => setTf(e.target.value)}>
              <option value="1d">日足</option>
              <option value="1wk">週足</option>
              <option value="1mo">月足</option>
            </select>
          </label>
          <label>
            表示期間
            <select value={range} onChange={(e) => setRange(e.target.value)}>
              <option value="6mo">6か月</option>
              <option value="2y">2年</option>
              <option value="5y">5年</option>
              <option value="all">取得範囲</option>
            </select>
          </label>
        </div>
        <div className="watch" aria-label="お気に入り">
          {watch.map((x) => (
            <button key={x} onClick={() => setSymbol(x)}>
              {x}
            </button>
          ))}
        </div>
      </header>
      <main>
        {status && (
          <div className="notice" role="status">
            {status}
          </div>
        )}
        {data && (
          <>
            <section className="metadata">
              <strong>{data.symbol}</strong>
              <span>
                最終確定足: {data.metadata.latest_final_session ?? "なし"}
              </span>
              <span>取得: {data.metadata.fetched_at ?? "不明"}</span>
              <span>{data.metadata.price_basis}</span>
              <span>遅延: 不明</span>
              {data.provisional_bars.length > 0 && <b>当日足は暫定</b>}
              {data.data_mode === "synthetic" && (
                <b>合成データ・実在銘柄ではありません</b>
              )}
            </section>
            <Chart data={data} selected={selected} visibleSma={sma} />
            <section className="panels">
              <div>
                <h2>支持・抵抗帯</h2>
                {data.zones.length ? (
                  data.zones.map((z, i) => (
                    <p key={i}>
                      {z.role} ¥{z.lower.toFixed(1)}–{z.upper.toFixed(1)}（
                      {z.touches}接触）
                    </p>
                  ))
                ) : (
                  <p>検出なし</p>
                )}
              </div>
              <div>
                <h2>パターン候補</h2>
                {data.patterns.length ? (
                  data.patterns.slice(0, 3).map((p) => (
                    <button
                      className="pattern"
                      key={p.id}
                      onClick={() => setSelected(p)}
                    >
                      {labels[p.type] ?? p.type}
                      <small>
                        {p.direction} / {p.state}
                      </small>
                    </button>
                  ))
                ) : (
                  <p>該当パターンなし</p>
                )}
                {data.patterns.length > 3 && (
                  <p>ほか {data.patterns.length - 3}件</p>
                )}
              </div>
            </section>
            {selected && (
              <aside className="sheet">
                <button
                  aria-label="詳細を閉じる"
                  onClick={() => setSelected(null)}
                >
                  ×
                </button>
                <h2>{labels[selected.type]}</h2>
                <p>
                  方向候補: {selected.direction} / 状態: {selected.state}
                </p>
                <p>反転観測: {selected.reaction_state}</p>
                <p>rule_version: {selected.rule_version}</p>
                {selected.anchors.map((a) => (
                  <p key={a.label}>
                    {a.label}: {a.date} ¥{a.price.toFixed(2)}（認識 {a.known_at}
                    ）
                  </p>
                ))}
              </aside>
            )}
          </>
        )}
      </main>
      {panel && (
        <aside className="sheet">
          <button aria-label="設定を閉じる" onClick={() => setPanel(null)}>
            ×
          </button>
          {panel === "settings" ? (
            <>
              <h2>設定</h2>
              <label>
                <input
                  type="checkbox"
                  checked={sma.sma75}
                  onChange={(e) =>
                    saveSettings({ ...sma, sma75: e.target.checked })
                  }
                />
                75日SMA
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={sma.sma200}
                  onChange={(e) =>
                    saveSettings({ ...sma, sma200: e.target.checked })
                  }
                />
                200日SMA
              </label>
              <button className="danger" onClick={removeLocal}>
                ローカルデータを削除
              </button>
            </>
          ) : (
            <>
              <h2>データとライセンス</h2>
              <p>
                価格は配当・分割調整後です。遅延はProvider公表値がない場合「不明」です。取得失敗時に合成値へ切り替えません。
              </p>
              <p>
                Lightweight
                Charts、React、FastAPI、yfinance等は各ライセンスに従います。パターンは独自ルール
                screening_v1 です。
              </p>
            </>
          )}
        </aside>
      )}
      <footer>
        予測・売買助言ではありません。形の条件成立と反転確認は別です。
      </footer>
    </>
  );
}
