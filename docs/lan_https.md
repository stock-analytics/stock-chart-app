# 任意LANモード（HTTPS必須）

LANモードは既定で無効です。PCとiPhoneが信頼できる個人LAN上にあり、OSファイアウォールで対象LANだけを許可できる場合に限ります。ルーターのポート転送やインターネット公開は禁止です。

1. `python scripts/set_password.py` の出力を `.env` の `LAN_PASSWORD_HASH` に保存する。
2. `python -c "import secrets; print(secrets.token_urlsafe(48))"` の出力を `SESSION_SECRET` に保存する。
3. `mkcert` 等でPCのLANホスト名/IPを含む証明書を生成し、iPhoneへCAを本人操作でインストール・信頼設定する。秘密鍵はリポジトリへ置かない。
4. `LAN_MODE=true` と `ALLOWED_HOSTS=pc-name.local,192.168.x.x` を設定する。
5. `uvicorn backend.app.main:app --host <LAN-IP> --port 8443 --ssl-keyfile <key> --ssl-certfile <cert>` で起動する。
6. `/login` からログインする。セッションCookieはHttpOnly/SameSite=Strict/Secure、変更APIは `X-CSRF-Token` が必要である。

HTTP、未認証、許可外Host/Origin、CSRF不一致は拒否されます。ログインは同一クライアントにつき15分に5回までです。
