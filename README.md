# webapi-sample-python

## English README

This is a sample to acquire data from JINS MEME web api (OAuth2).

### Install dependant library

pip install oauthlib 

### data_fetch.py

This sample acquires 15-second interval data and 60-second interval data according to the OAuth2 authorization code flow and saves them in CSV.

- client_id / client_secret / redirect_uri are obtained from the JINS MEME Developers app list and rewritten.
- Set the range of the date and time you want to fetch to the data start datetime (date_from) and data end datetime (date_to) in the parameters.
- Run `python data_fetch.py`.
- (You will see a message that the redirect URL is inaccessible because you have not set up a web server for the redirect URL, but this is not a problem)
- Copy and paste the URL(contains grant code) in the address bar into the Python REPL
- The data is retrieved, converted to a pandas dataframe, and saved as CSV (15s_interval_data.csv, 60s_interval_data.csv)

## Japanese README

JINS MEME のWeb api(OAuth2)からのデータ取得をするサンプルです。

### モジュールのインストール

pip install oauthlib 

### data_fetch.py

OAuth2の認可コードフローに沿って15秒間隔データ、60秒間隔データを取得しCSVに保存するサンプルです。

- client_id / client_secret / redirect_uri はJINS MEME Developers のアプリ一覧から取得し、書き換えます
- paramのデータ開始日(date_from)とデータ終了日(date_to)に取得したい日時のレンジをセットします
- `python data_fetch.py` を実行します
- 認可コードフローなのでブラウザが開きアドレスバーにリダイレクトURLが表示されます(リダイレクトURLにWebサーバーを設定していないのでアクセスできないとの表示がでますが、問題ありません)
- アドレスバーのURL(grant codeが含まれます)をPythonのREPLにコピペします
- データが取得され、pandas dataframeに変換し、CSV(15s_interval_data.csv, 60s_interval_data.csv)として保存します
