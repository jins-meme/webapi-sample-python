"""
JINS MEME Web API Sample for python
(c) JINS Inc, 2022
"""

import urllib.request
import json
from oauthlib.oauth2 import WebApplicationClient
import webbrowser
import pandas as pd

#JINS MEME API 固有値
token_url = 'https://apis.jins.com/meme/v1/oauth/token'
auth_url = 'https://accounts.jins.com/jp/ja/oauth/authorize'
logicdata_url = 'https://apis.jins.com/meme/v2/users/me/official/computed_data'
summarydata_url = 'https://apis.jins.com/meme/v2/users/me/official/standard_mode_logs'
scope = ['official']
state = 'somestate'
response_type = 'code'
service_id = 'meme'

#JINS MEME Developers のアプリ一覧から取得できる値
client_id = 'your_client_id'
client_secret = 'your_client_secret'
redirect_uri = 'https://localhost:5001' #使用しているライブラリでhttpsが必須です

#データ取得レンジ、1日以内をセットしてください
params = {
    'date_from': '2022-05-19T09:00:00+09:00',
    'date_to': '2022-05-19T14:59:59+09:00',
}

#クライアントの作成
oauth = WebApplicationClient(client_id)

#認証リクエストの作成
url, headers, body = oauth.prepare_authorization_request(
    auth_url,
    redirect_url=redirect_uri,
    scope=scope,
    state=state,
    service_id=service_id
)

#認可URLをブラウザで開き、リダイレクトされる
webbrowser.open(url, new=0, autoraise=True)

#リダイレクト先のURL(パラメター全て含め)をPythonのREPLにコピペする
authorization_response = input('Press Enter Browser URL: ')

#tokenのリクエストを作成
url, headers, body = oauth.prepare_token_request(token_url, authorization_response, redirect_uri, client_secret=client_secret)
#print(url)
#print(headers)
#print(body)

#tokenリクエストを実行し、成功するとoauthに格納される
req = urllib.request.Request(url, body.encode(), headers=headers)
with urllib.request.urlopen(req) as res:
    oauth.parse_request_body_response(res.read())

"""
15秒データの取得とCSV保存
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
def get_15s_interval_data(url, headers, cursor=None):
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
            get_15s_interval_data(url, headers, cursor=raw["cursor"])
        else:
            print("cursor none, fetch end")

#取得の実行
#15秒間隔データのリクエストの作成
url = logicdata_url + '?' + urllib.parse.urlencode(params)
url, headers, body = oauth.add_token(url)
headers['Accept'] = 'application/json' #必要なので追加します

get_15s_interval_data(url, headers)
#print(data_15s_interval_df.info())

#取得データの保存
data_15s_interval_df.to_csv('15s_interval_data.csv', index=False)


"""
60秒データの取得とCSV保存
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
def get_60s_interval_data(url, headers, cursor=None):
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
            get_60s_interval_data(url, headers, cursor=raw["cursor"])
        else:
            print("cursor none, fetch end")

#取得の実行
#60秒間隔データのリクエストの作成
url = summarydata_url + '?' + urllib.parse.urlencode(params)
url, headers, body = oauth.add_token(url)
headers['Accept'] = 'application/json' #必要なので追加します

get_60s_interval_data(url, headers)
#print(data_60s_interval_df.info())

#取得データの保存
data_60s_interval_df.to_csv('60s_interval_data.csv', index=False)


