# IT Industry Data Assistant

한국 IT/SI 관련 산업의 월별 서비스업생산지수와 IT 직종 구인 수요를 분석하는 시계열 분석 프로젝트이다.

## 1. 프로젝트 목적

본 프로젝트의 목적은 한국 IT/SI 업계의 산업 활동 흐름과 인력 수요가 장기적으로 어떻게 변했는지 확인하는 것이다.

분석 질문은 다음과 같다.

1. IT/SI 관련 서비스업생산지수에 특정 월, 특히 3월 집중 현상이 있는가?
2. 장기 추세는 성장했는가? 코로나19 참고 구간에서 꺾임이 있었는가?
3. 세부 IT 업종별 계절성은 다른가?
4. IT 직종 구인 수요는 SI 관련 생산지수와 같은 방향으로 움직이는가? 선행/후행 관계가 있는가?
5. 전년동월 Seasonal Naive 예측은 어느 시점에서 크게 빗나가는가?

## 2. 사용 데이터

### 2.1 서비스업생산지수

- 출처: KOSIS / 통계청
- 통계: 서비스업동향조사 서비스업생산지수
- 기간: 2017.01 ~ 2026.08
- 주기: 월
- 기본 지표: 불변지수
- 비교 지표: 경상지수

대상 업종:

- 정보통신업
- 소프트웨어 개발 및 공급업
- 컴퓨터 프로그래밍, 시스템 통합 및 관리업
- 정보서비스업

### 2.2 구인 수요

- 출처: 한국고용정보원 고용행정통계
- 통계: 직종별 구인구직취업현황(월)
- 기간: 2017.01 ~ 2026.08
- 주기: 월

분석 지표:

- 상위 IT 직종 전체 구인인원
- 소프트웨어 개발자 구인인원
- 구인인원 / 구직건수 비율

## 3. 저장소 구조

```text
.
├── DATA_SOURCE.md
├── README.md
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

주의: 원본 및 가공 CSV/XLS/XLSX 파일은 라이선스 확인 전까지 Git에 포함하지 않는다. 데이터 다운로드 방법은 `DATA_SOURCE.md`를 참고한다.

## 4. 실행 방법

### 4.1 환경 준비

```zsh
python3 -m venv .venv
```

```zsh
source .venv/bin/activate
```

```zsh
pip install -r requirements.txt
```

현재 분석 코드는 `pandas`와 `matplotlib` 중심으로 작성되어 있다.

### 4.2 원본 데이터 준비

`DATA_SOURCE.md` 안내에 따라 원본 파일을 내려받아 다음 폴더에 둔다.

```text
data/raw/
```

필요한 원본 데이터는 다음 두 종류이다.

1. KOSIS 월별 서비스업생산지수 CSV
2. 고용행정통계 직종별 구인구직취업현황 월별 엑셀 파일

### 4.3 전처리 실행

```zsh
python3 src/preprocess.py
```

생성 파일:

```text
data/processed/service_production_long.csv
data/processed/job_demand_long.csv
data/processed/merged_monthly.csv
```

### 4.4 분석 및 시각화 실행

```zsh
python3 src/analyze.py
```

생성 이미지:

```text
images/01_service_trend_constant_index.png
images/02_monthly_seasonality_by_industry.png
images/03_current_vs_constant_index.png
images/04_service_vs_job_demand_indexed.png
images/05_seasonal_naive_forecast_error.png
images/06_lag_correlation_service_vs_jobs.png
```

## 5. 주요 결과 요약

자세한 내용은 `REPORT.md`에 정리했다.

핵심 결과는 다음과 같다.

- 3월 집중 현상은 확인되지 않았다.
- `컴퓨터 프로그래밍, 시스템 통합 및 관리업`의 불변지수는 2017.01 대비 2026.08에 약 83.8% 증가했다.
- SI 관련 업종은 비교 대상 IT 업종 중 월별 변동성이 가장 컸다.
- IT 구인수요와 SI 관련 생산지수는 동월 및 ±6개월 시차 기준에서 뚜렷한 양의 상관을 보이지 않았다.
- 전년동월 Seasonal Naive 예측은 일부 달에서 15% 내외 오차를 보였다.

## 6. 결과물

- 분석 보고서: `REPORT.md`
- AI 사용 로그: `ai-log.md`
- 컬럼 매핑: `data/columns.md`
- 전처리 코드: `src/preprocess.py`
- 분석 코드: `src/analyze.py`

## 7. 한계

- 서비스업생산지수는 매출액이 아니라 산업 활동 수준을 나타내는 지표이다.
- 고용행정통계의 직종분류가 2007/2018/2025 체계로 변경되어 장기 비교에 한계가 있다.
- 구인인원/구직건수 비율은 공식 구인배율이 아니다.
- 코로나19 구간은 참고 구간으로 사용했으며, 인과관계를 증명한 것은 아니다.
