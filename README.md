# Chart Lens

日本株の日足データを取得・保存し、日／週／月のチャート、移動平均、支持・抵抗帯、チャートパターン候補を表示する**個人利用専用**Webアプリです。売買助言、利益予測、自動注文、データ再配信を行いません。唯一の実装基準は [`docs/implementation_spec.md`](docs/implementation_spec.md) です。

> **注意**: yfinance は Yahoo 公認ではなく、取得データの利用条件とライブラリのライセンスは別です。実データは個人研究目的に限り、提供元の条件を確認してください。取得失敗時に架空データへ切り替えません。合成データは `DEMO_` 銘柄を明示した場合だけ利用されます。

## 必要環境

- Python 3.11〜3.14
- Node.js 20以上、npm 10以上
- macOS または Linux

## 導入

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
cd frontend && npm ci && cd ..
```

依存導入にはインターネット接続が必要です。以後の起動スクリプトは依存を更新しません。

## 開発起動・停止

端末1:

```bash
. .venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

端末2:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

`http://127.0.0.1:5173` を開き、初期値 `DEMO_7203` で合成モードを確認します。停止は各端末で `Ctrl-C` です。DB は `data/chart-lens.sqlite3` に作成されます。

## 本番ビルド

```bash
cd frontend && npm run build && cd ..
. .venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

ビルド後は FastAPI が `frontend/dist` を同一Originで配信します。既定では localhost 以外に公開しません。

## 実データ

`DATA_MODE=live` で使う Provider 実装は `backend/app/providers/yahoo.py` です。`auto_adjust=False, actions=True, repair=False` を固定しています。`DATA_MODE=synthetic`（既定）では合成Providerだけ、`DATA_MODE=live` ではyfinance Providerだけを有効化します。実データProviderの運用接続は未検証です。接続エラー時の自動フォールバックはありません。

## DB移行・削除

起動時にバージョン付きスキーマがトランザクションで初期化されます。WAL と `busy_timeout=5000` を設定します。ローカルデータ削除は停止後に次を実行します。

```bash
rm -f data/chart-lens.sqlite3 data/chart-lens.sqlite3-shm data/chart-lens.sqlite3-wal
```

## テスト

```bash
cd backend && pytest -q
python -m compileall -q backend
cd frontend && npm test
cd frontend && npm run build
```

ネットワーク不要のPythonテストは合成OHLCを使います。ブラウザE2E、iPhone実機、実市場接続の結果は [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) を参照してください。

## PWA と iPhone

manifest、アイコン、アプリ殻だけを保存するservice workerを含みます。`/api/` は一切キャッシュしません。localhost以外でのPWA利用には信頼済みHTTPSが必要です。LANモードは明示設定時だけ有効になり、認証・CSRF・HTTPSを必須にします。単に `0.0.0.0` で起動したりルーターのポートを開放したりしないでください。

## 構成

- `backend/app/providers`: 実データ／合成データ境界と入力検証
- `backend/app/analysis`: 集約、SMA、ATR、ピボット、帯、パターン
- `backend/app/storage`: SQLiteスキーマと不変snapshot
- `frontend`: React、TypeScript、Lightweight Charts、PWA
- `backend/tests`: 決定的なオフライン単体・結合試験
- `docs/implementation_spec.md`: DOCXから省略せず変換した仕様

## ライセンス

本リポジトリ固有コードは個人利用目的です。依存ライブラリは各プロジェクトのライセンスに従います（React/Vite/FastAPI/pandas/NumPy/yfinance/Lightweight Charts等）。TradingView Lightweight Chartsを利用する際は同プロジェクトの帰属表示要件を確認してください。パターン名称・教材・データの商用利用可否を本READMEは保証しません。

## 任意LANモード

任意LANモードには、PBKDF2パスワード、署名付きHttpOnly/SameSiteセッションCookie、CSRFトークン、15分5回のログイン制限、HTTPS強制、Host/Origin許可リストを実装しています。既定は無効です。証明書作成、iPhoneへのCA導入、ファイアウォールを含む手順は [`docs/lan_https.md`](docs/lan_https.md) を参照してください。HTTPだけでのLAN公開やルーターのポート転送は行わないでください。
