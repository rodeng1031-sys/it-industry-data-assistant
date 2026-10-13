# IT Industry Data Assistant

韓国のIT/SI関連産業について、月次サービス業生産指数とIT職種の求人需要を用いて時系列分析を行うプロジェクトである。

## 1. プロジェクトの目的

本プロジェクトの目的は、韓国IT/SI産業の活動水準とIT人材需要が長期的にどのように変化してきたかを確認することである。

主な分析課題は以下の通りである。

1. IT/SI関連サービス業生産指数に特定月、特に3月への集中傾向があるか。
2. 長期的なトレンドは成長しているか。COVID-19参考期間に落ち込みが見られるか。
3. IT関連の細分類産業ごとに季節性は異なるか。
4. IT職種の求人需要はSI関連生産指数と同じ方向に動くか。先行・遅行関係はあるか。
5. 前年同月値を用いるSeasonal Naive予測は、どの時点で大きく外れるか。

## 2. 使用データ

### 2.1 サービス業生産指数

- 出所: KOSIS / 韓国統計庁
- 統計: サービス業動向調査 サービス業生産指数
- 期間: 2017年1月 ~ 2026年8月
- 周期: 月次
- 基本指標: 不変指数
- 比較指標: 経常指数

対象産業は以下の4つである。

- 情報通信業
- ソフトウェア開発及び供給業
- コンピュータプログラミング、システム統合及び管理業
- 情報サービス業

本分析では、SIに最も近い産業として「コンピュータプログラミング、システム統合及び管理業」を中心に扱う。

### 2.2 IT職種の求人需要

- 出所: 韓国雇用情報院 雇用行政統計
- 統計: 職種別 求人・求職・就業現況（月次）
- 期間: 2017年1月 ~ 2026年8月
- 周期: 月次

分析に用いた求人需要指標は以下の2つである。

| 分析指標 | 内容 |
|---|---|
| it_broad | 情報通信関連の上位職種全体 |
| software_developer | ソフトウェア開発者関連職種 |

注意点として、職種分類は2007年分類、2018年分類、2025年分類が混在している。そのため、最も類似した職種を接続して長期時系列を作成したが、分類変更の影響が含まれる可能性がある。

## 3. リポジトリ構成

```text
.
├── DATA_SOURCE.md
├── README.md
├── README_ja.md
├── REPORT.md
├── ai-log.md
├── data/
│   ├── columns.md
│   ├── raw/
│   └── processed/
├── images/
├── requirements.txt
└── src/
    ├── preprocess.py
    └── analyze.py
```

原本データおよび加工済みCSV/XLS/XLSXファイルは、ライセンス確認前のためGitには含めない。データの取得方法は `DATA_SOURCE.md` を参照する。

## 4. 実行方法

### 4.1 環境構築

```zsh
python3 -m venv .venv
```

```zsh
source .venv/bin/activate
```

```zsh
pip install -r requirements.txt
```

### 4.2 原本データの準備

`DATA_SOURCE.md` の案内に従って、必要な原本データをダウンロードし、以下のフォルダに保存する。

```text
data/raw/
```

必要な原本データは以下の2種類である。

1. KOSIS 月次サービス業生産指数 CSV
2. 雇用行政統計 職種別求人・求職・就業現況 月次Excelファイル

### 4.3 前処理

```zsh
python3 src/preprocess.py
```

生成されるファイル:

```text
data/processed/service_production_long.csv
data/processed/job_demand_long.csv
data/processed/merged_monthly.csv
```

### 4.4 分析・可視化

```zsh
python3 src/analyze.py
```

生成される図表:

```text
images/01_service_trend_constant_index.png
images/02_monthly_seasonality_by_industry.png
images/03_current_vs_constant_index.png
images/04_service_vs_job_demand_indexed.png
images/05_seasonal_naive_forecast_error.png
images/06_lag_correlation_service_vs_jobs.png
```

## 5. 主な分析結果

詳細は `REPORT.md` に整理した。

主な結果は以下の通りである。

1. 3月への集中傾向は確認されなかった。
2. 「コンピュータプログラミング、システム統合及び管理業」の不変指数は、2017年1月から2026年8月までに約83.8%上昇した。
3. SI関連産業は、比較対象のIT関連産業の中で月次変動が最も大きかった。
4. IT求人需要とSI関連生産指数の間には、同月比較および±6か月のラグ比較において明確な正の相関は見られなかった。
5. 前年同月値を用いたSeasonal Naive予測では、一部の月で15%前後の誤差が発生した。

## 6. 分析上の制約

- サービス業生産指数は売上高そのものではなく、産業活動水準を示す指数である。
- 職種別求人データは分類体系の変更があり、長期比較には注意が必要である。
- 求人数 / 求職件数の比率は、本分析用に計算した指標であり、公式な求人倍率ではない。
- COVID-19期間は参考期間として扱っており、因果関係を証明したものではない。

## 7. 関連文書

- 韓国語README: `README.md`
- データ取得方法: `DATA_SOURCE.md`
- 分析報告書: `REPORT.md`
- AI使用ログ: `ai-log.md`
