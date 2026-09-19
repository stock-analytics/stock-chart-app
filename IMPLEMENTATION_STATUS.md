# 実装・検証状況

更新日: 2026-09-19。実装、ネットワーク不要の自動テスト、外部環境での受入検証を分けて記録する。

## M0〜M5

| 工程 | 実装 | 自動テスト | 外部環境 |
| --- | --- | --- | --- |
| M0 | 実装済み：Provider境界、入力/品質検査、不変snapshot、SQLite migration、合成モード | 合格 | yfinance実接続は未検証 |
| M1 | 実装済み：日週月、日足SMA、ATR、pivot、支持/抵抗、チャネル、ダブル形、座標ベース描画 | 合格 | ブラウザ操作は未検証 |
| M2 | 実装済み：強気/弱気Crab、XABC候補帯、stable family、永続イベント | 合格 | 実市場で未検証 |
| M3 | 実装済み：三重天底、三尊、三角3種、ウェッジ2種、旗/ペナント両方向、カップ、共通状態遷移 | 合格 | 実市場で未検証 |
| M4 | 実装済み：Deep Crab/Gartley/Bat/Butterfly両方向、比率・配置・候補帯 | 合格 | 実市場で未検証 |
| M5 | 実装済み：設定、お気に入り、削除確認、PWA、任意LAN認証/CSRF/HTTPS強制/試行制限、日本語文書 | 合格 | npm build、Playwright、iPhone、実HTTPS証明書は未検証 |

## T01〜T23

| ID | 状態 | 結果 |
| --- | --- | --- |
| T01 | テスト合格 | SMA 29/30、75、200、手計算 |
| T02 | テスト合格 | 週/月OHLCV、null volume、暫定状態、2024休場日 |
| T03 | テスト合格 | 週足表示が日足SMAを利用 |
| T04 | テスト合格 | 調整係数、欠落/NaN、同値・異値重複 |
| T05 | テスト合格 | known_at、同値右端、high/low二重除外 |
| T06 | テスト合格 | prefix前はforming、突破後のみ成立 |
| T07 | テスト合格 | snapshot/as_of決定性、表示range非依存 |
| T08 | テスト合格 | 全通常type、日週月、forming/成立/無効/期限 |
| T09 | テスト合格 | 全5ハーモニック、ゼロ分母、配置不正 |
| T10 | テスト合格 | 固定比率±3%境界、Crab/Deep Crab分離、PRZ計算 |
| T11 | テスト合格 | zone_touched/D_confirmed/reversal_observed分離 |
| T12 | テスト合格 | timeout再試行、429 cooldown、mock非代入 |
| T13 | テスト合格 | 週末、当日暫定、calendar_unknown |
| T14 | 実装済み・実機未検証 | 日時/価格座標、ResizeObserver。パン/回転はブラウザ未検証 |
| T15 | テスト合格 | request IDで古い非同期応答を破棄 |
| T16 | 実装済み・実機未検証 | 44px、レスポンシブ、ARIA。実ブラウザ幅/読上げ未検証 |
| T17 | テスト合格 | symbol、URL/SQL片、Host/Origin、未認証LAN拒否 |
| T18 | テスト合格 | service workerのAPI除外、オフライン明示 |
| T19 | 未検証 | README手順は実装済み。レジストリ制限によりクリーン導入未検証 |
| T20 | テスト合格 | rule別family、不変イベント、重複抑止 |
| T21 | テスト合格 | catalog全21 type=true、通常/ハーモニックを日週月で実行 |
| T22 | テスト合格 | 探索上限、警告、同symbol同時取得統合 |
| T23 | 実装済み・実機未検証 | PBKDF2、Cookie、CSRF、HTTPS強制、試行制限。iPhone未検証 |

未検証項目は外部ネットワーク、ブラウザ、証明書、端末を必要とする受入試験だけであり、該当機能コードとオフラインテストは収録済みである。
