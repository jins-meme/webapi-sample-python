"""
連結したDFを受取り、各種モジュールで表示する描画オブジェクトに変換して返すクラス
Copyright © 2022 Taiki Komoda and JINS Inc., All rights reserved.

ver. 20220915
"""
import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats as stats

# 90% Percentile
def q90(x):
    return x.quantile(0.9)

# 99% Percentile
def q99(x):
    return x.quantile(0.99)

# kde max
def kde_max(x):
    #npでフィッティング
    nparam_density = stats.gaussian_kde(x)
    #x作る
    aryx = np.linspace(0, 200, 201)
    #y作る
    aryy = nparam_density(aryx)   
    
    #y最大の引数をx配列に渡してxの取得
    return aryx[aryy.argmax()]

class CalcStandardData:
    #def __init__(self):

    """
    基本的なフィルタとデータ加工を行うメソッド

    Arguments:
        df: data frame, summaryData(60秒間隔データ)
        start_hour: int, 集計開始時間、7とすると7時以降のデータのみ抽出される、フィルタしない場合は0を指定
        end_hour: int, 集計終了時間、20とすると20時以前のデータのみ抽出される、フィルタしない場合は23を指定
    
    Returns:
        total_df: data frame, 基本フィルタ、時間フィルタを実施したのみのデータフレーム
        quiet_df: data frame, 上記に加えノイズ時間でフィルタしたデータフレーム
        metric_df: data frame, 日別のメトリックにgroupしたデータフレーム
    """
    def cleansingAndSummarize(self, df, start_hour, end_hour):
        #基本クレンジング
        data_df = df.query("wea_s >= 20 & tl_yav >= -45 & tl_yav <= 90 & tl_xav >= -45 & tl_xav <= 45").copy()

        #時間フィルタ
        data_df['datetime'] = pd.to_datetime(data_df.date)
        data_df['datestr'] = data_df['datetime'].dt.tz_convert('Asia/Tokyo').dt.strftime('%Y-%m-%d')
        data_df['hour'] = data_df['datetime'].dt.tz_convert('Asia/Tokyo').dt.strftime('%H').astype(int)
        data_df['minutes'] = data_df['datetime'].dt.tz_convert('Asia/Tokyo').dt.strftime('%M').astype(int)
        data_df["em_rl"] = data_df["ems_rl"] + data_df["eml_rl"]
        
        data_df["stp"] = data_df["stp_fst"] + data_df["stp_mid"] + data_df["stp_slw"] + data_df["stp_vsl"]
        data_df["stp_log10"] = np.log10(data_df["stp"] + 1) # +1はlog取る用
        data_df["hm_tot"] = data_df["hm_yo"] + data_df["hm_po"] + 1 # +1はlog取る用
        data_df["activeness"] = np.where(data_df["stp"] >= 20, data_df["stp"], np.where(data_df["hm_tot"] >= 20, 20, data_df["hm_tot"]))
        data_df["activeness_log10"] = np.log10(data_df["activeness"])
        
        total_df = data_df.query("hour >= " + str(start_hour) + " & hour <= " + str(end_hour))
        quiet_df = total_df.query("nis_s <= 10")
        #print(quiet_df)
        
        #パーテション毎にPercentileを取る
        # groupby(["datestr"], as_index=False
        em_df = quiet_df[["datestr", "em_rl"]].groupby(["datestr"]).agg(em_kmax = ('em_rl', kde_max))
        hm_df = total_df[["datestr", "hm_yo"]].groupby(["datestr"]).agg(hm_q90 = ('hm_yo', q90), hm_q99 = ('hm_yo', q99))
        
        metric_df = hm_df.merge(em_df, left_index=True, right_index=True).reset_index()
        #print(str(len(total_df)) + " " + str(len(quiet_df)) + " " + str(len(metric_df)))

        #中間値を保存しておく処理とか必要になってくる時がくるかも
        return total_df, quiet_df, metric_df

    """
    ヒートマップ描画用のデータフレームを作成するメソッド

    Arguments:
        _df: data frame, summaryData(60秒間隔データ)
        _minutes: Object(string), 何分毎にサマルか, 60で割り切れる数字が望ましい
        _index: Object(string), "act"(歩数に加え、低歩数時は頭部運動回数を当てた総合指標)か"stp"(歩数のみ)
        _scale: Object(string), "lin"か'log'
        _function: Object(string),  "max"か"mean"
    
    Returns:
        ヒートマップ描画用のデータフレーム
    """
    def createHeatmapPivotData(self, _df, _minutes, _index, _scale, _function):
        #分group用の列追加
        _df["minutes_group"] = np.floor(_df["minutes"] / int(_minutes)) * int(_minutes)
        _df["hhmm_group"] = _df["hour"] + _df["minutes_group"] / 60

        #サマリ分でグループ化
        grouped_df = _df.groupby(["datestr", "hhmm_group"]).agg(  #[["datestr", "hhmm_group", "activeness_log10"]]
            act_log_mean = ('activeness_log10', np.mean), act_log_max = ('activeness_log10', np.max),
            act_lin_mean = ('activeness', np.mean), act_lin_max = ('activeness', np.max),
            stp_log_mean = ('stp_log10', np.mean), stp_log_max = ('stp_log10', np.max),
            stp_lin_mean = ('stp', np.mean), stp_lin_max = ('stp', np.max),
        ).reset_index()
        #print(grouped_df)

        #対象とする指標名の指定
        index_name = _index + '_' + _scale + '_' + _function

        pivot_table = grouped_df.pivot("datestr", "hhmm_group", index_name)
        #print(pivot_table)

        return pivot_table