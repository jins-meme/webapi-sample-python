"""
Activities heatmap sample
(c) JINS Inc, 2022
"""

import pandas as pd
import plotly.express as px
from jinsmeme import calcstd

calcStandardData = calcstd.CalcStandardData()

#複数ファイルに別れている場合は結合する
df1 = pd.read_csv("summary_data_00.csv") #実際のデータファイルに変更してください
df2 = pd.read_csv("summary_data_01.csv") #実際のデータファイルに変更してください
df3 = pd.read_csv("summary_data_02.csv") #実際のデータファイルに変更してください
#...
df = pd.concat([df1, df2, df3])
print(df)

#データの基本クレンジング
dfAry = calcStandardData.cleansingAndSummarize(df, 0, 23)
#描画用にピボット
pivotTable = calcStandardData.createHeatmapPivotData(dfAry[0], "5", "act", "lin", "max")    
fig = px.imshow(pivotTable)
fig.update_yaxes(type="category") #これを設定しないと日付が連続でない時に勝手に補完される

fig.show()