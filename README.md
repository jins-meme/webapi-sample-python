# webapi-sample-python

JINS MEME のWeb api(OAuth2)からのデータ取得や、グラフを描画するサンプルです。

## 準備

pip install oauthlib 

## data_fetch.py

OAuth2の認可コードフローに沿って15秒間隔データ、60秒間隔データを取得しCSVに保存するサンプルです。

- client_id / client_secret / redirect_uri はJINS MEME Developers のアプリ一覧から取得し、書き換えます
- paramのデータ開始日(date_from)とデータ終了日(date_to)に取得したい日時のレンジをセットします
- `python data_fetch.py` を実行します
- 認可コードフローなのでブラウザが開きアドレスバーにリダイレクトURLが表示されます(リダイレクトURLにWebサーバーを設定していないのでアクセスできないとの表示がでますが、問題ありません)
- アドレスバーのURLをPythonのREPLにコピペします
- データが取得され、pandas dataframeに変換し、CSV(data.csv)として保存します
