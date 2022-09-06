"""
JINS MEME Web API Sample for python
(c) JINS Inc, 2022
"""

import urllib.request
import json
from oauthlib.oauth2 import WebApplicationClient
import webbrowser
import pandas as pd

import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import sys
import datetime

#JINS MEME API 固有値
token_url = 'https://apis.jins.com/meme/v1/oauth/token'
auth_url = 'https://accounts.jins.com/jp/ja/oauth/authorize'
logicdata_url = 'https://apis.jins.com/meme/v2/users/me/official/computed_data'
summarydata_url = 'https://apis.jins.com/meme/v2/users/me/official/standard_mode_logs'
scope = ['official']
state = 'somestate'
response_type = 'code'
service_id = 'meme'

#JINS MEME Developers サイトから取得して以下をセットしてください
client_id = ''
client_secret = ''
redirect_uri = 'https://localhost:5001' #ここで使用しているライブラリではhttpsが必須です

#データ取得日付レンジ、0埋めしてください
fetch_from = '2022-08-28'
fetch_to = '2022-09-05'

#localサーバーまわりの設定項目
port = 5001 #redirect_uriのポートと一致させるのと、ローカル環境で同じポートでソフトウェアが動作していないことを確認してください。
certfile = "./localhost.pem" # 予め証明書を作成しておいてください。

"""
grant codeを受け取った後の処理

以下のコードはローカルサーバーでブラウザからのアクセスを受取り、
grant codeを取得してtoken取得→データ取得→プログラム終了を行うので
認可URLが発行される前にセットしておく必要があります
"""
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        #token取得
        get_token_request(redirect_uri + self.path)

        d1 = datetime.date(int(fetch_from[0:4]),int(fetch_from[5:7]),int(fetch_from[8:10]))
        d2 = datetime.date(int(fetch_to[0:4]),int(fetch_to[5:7]),int(fetch_to[8:10]))

        # 複数日付分取得する
        for i in range((d2 - d1).days + 1):
            dateTmp = d1 + datetime.timedelta(i)
            print('Processing ' + dateTmp.strftime('%Y-%m-%d'))
            params = {
                'date_from': dateTmp.strftime('%Y-%m-%d') + 'T00:00:00+09:00',
                'date_to': dateTmp.strftime('%Y-%m-%d') + 'T23:59:59+09:00',
            }

            #取得の実行
            get_15s_interval_data(params)
            get_60s_interval_data(params)

        #取得データの保存
        data_15s_interval_df.to_csv('15s_interval_data.csv', index=False)
        data_60s_interval_df.to_csv('60s_interval_data.csv', index=False)
        #スレッドが活きているのでプログラムを終了する
        sys.exit()

        #overrideする
        SimpleHTTPRequestHandler.do_GET(self)

# grant code を受け取る https サーバーを起動しておきます
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile)
httpd = HTTPServer(('', port), Handler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
server_thread = threading.Thread(target=httpd.serve_forever) 
# server_thread.daemon = True
server_thread.start()

"""
認可URLを取得するところまでの処理

こちらが起点になります
"""
# oauthクライアントの作成
oauth = WebApplicationClient(client_id)

# 認証リクエストの作成
url, headers, body = oauth.prepare_authorization_request(
    auth_url,
    redirect_url=redirect_uri,
    scope=scope,
    state=state,
    service_id=service_id
)
#認可URLをブラウザで開き、リダイレクトされる
webbrowser.open(url, new=0, autoraise=True)

"""
tokenリクエスト関数
"""
def get_token_request(authorization_response):
    url, headers, body = oauth.prepare_token_request(token_url, authorization_response, redirect_uri, client_secret=client_secret)
    #print(url)
    #print(headers)
    #print(body)

    #tokenリクエストを実行し、成功するとoauthに格納される
    req = urllib.request.Request(url, body.encode(), headers=headers)
    with urllib.request.urlopen(req) as res:
        oauth.parse_request_body_response(res.read())

"""
15秒データの取得関数
"""
#結合・格納先dataframe
data_15s_interval_df = pd.DataFrame()

#1レスポンスのデータをdata_15s_interval_dfに追記する関数
def concat_15s_interval_data(res_data):
    #時間帯毎に属性が分かれるので、それぞれの時間帯をたどる
    for hour in res_data["computed_data"]:
        tmp_df = pd.DataFrame(res_data["computed_data"][hour])
        print("hour:" + hour + " len:" + str(len(tmp_df))) #統計情報の表示

        # グローバルのdfにconcatする
        global data_15s_interval_df
        data_15s_interval_df = pd.concat([data_15s_interval_df, tmp_df])

#15秒間隔データのリクエスト
def get_15s_interval_data(params, cursor=None):

    #15秒間隔データのリクエストの作成
    url = logicdata_url + '?' + urllib.parse.urlencode(params)
    url, headers, body = oauth.add_token(url)
    headers['Accept'] = 'application/json' #必要なので追加します

    #cursorがセットされている時はURLパラメターに追記する
    final_url = url + ("" if cursor is None else "&cursor=" + cursor)
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req) as res:
        #レスポンスのparse
        raw = json.load(res)

        #dataをくっつける
        concat_15s_interval_data(raw)

        #cursorがセットされていた場合、再帰でデータをリクエストする
        if raw["cursor"] is not None:
            print("cursor: " + raw["cursor"])
            get_15s_interval_data(params, cursor=raw["cursor"])
        else:
            print("cursor none, fetch end")

"""
60秒データの取得関数
"""
#結合・格納先dataframe
data_60s_interval_df = pd.DataFrame()

#1レスポンスのデータをdata_60s_interval_dfに追記する関数
def concat_60s_interval_data(res_data):
    #時間帯毎に属性が分かれるので、それぞれの時間帯をたどる
    for hour in res_data["standard_mode_logs"]:
        tmp_df = pd.DataFrame(res_data["standard_mode_logs"][hour])
        print("hour:" + hour + " len:" + str(len(tmp_df))) #統計情報の表示

        # グローバルのdfにconcatする
        global data_60s_interval_df
        data_60s_interval_df = pd.concat([data_60s_interval_df, tmp_df])

#60秒間隔データのリクエスト
def get_60s_interval_data(params, cursor=None):
    #60秒間隔データのリクエストの作成
    url = summarydata_url + '?' + urllib.parse.urlencode(params)
    url, headers, body = oauth.add_token(url)
    headers['Accept'] = 'application/json' #必要なので追加します

    #cursorがセットされている時はURLパラメターに追記する
    final_url = url + ("" if cursor is None else "&cursor=" + cursor)
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req) as res:
        #レスポンスのparse
        raw = json.load(res)

        #dataをくっつける
        concat_60s_interval_data(raw)

        #cursorがセットされていた場合、再帰でデータをリクエストする
        if raw["cursor"] is not None:
            print("cursor: " + raw["cursor"])
            get_60s_interval_data(params, cursor=raw["cursor"])
        else:
            print("cursor none, fetch end")
