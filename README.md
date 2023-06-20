# 単票をブラウザで表示する

## 請求書サンプル #1
* 用紙サイズ：A4（縦）
* ページ数：１ページ
* 消費税計算：あり

## 請求書サンプル #2
* 用紙サイズ：A4（縦）
* ページ数：１ページ
* 消費税計算：なし

## その他
* 入力データの自動保存（クッキー使用時のみ）

## 課題
* 2023/10から始まる予定のインボイス対応

### 使用しているパッケージ
* Flask (2.3.2)
* pdfkit（1.0.0）
* wkhtmltopdf (wkhtmltopdf 0.12.6.1 (with patched qt)) *1

*1：Termuxのubuntuでインストールする場合、```apt wkhtmltopdf``` でインストールしてはダメ
本家のサイトからDEBファイルをDLしてインストール（```sudo apt install -y ./wkhtmltox_0.12.6.1-2.jammy_arm64.deb```）すること。

## 利用規定
本ソフトの利用により発生した障害およびトラブルについては、一切の責任は負わないものとする。

## uwsgi 設定例 (uwsgi.ini)
```
[uwsgi]
base = プロジェクトへのパス/makePDFWeb
module = make_pdf_web:app

pythonpath = %(base)

callable = app
plugin = /usr/lib/uwsgi/plugins/python3_plugin.so
logto = ログのパス/make_pdf_web.log

master = true
processes = 1
threads = 1
http-socket = :8089
vacuum = true
pidfile = /run/user/uwsgi.pid
```

## nginx 設定例 (/etc/nginx/sites-available/default)
```
location ~ ^/make_pdf/.*$ {
        rewrite ^/make_pdf/(.*)$ /$1 break;
        include uwsgi_params;
        proxy_pass http://127.0.0.1:8089;
        proxy_set_header X-Forwarded-For $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Request-Path $request_uri;
}
```