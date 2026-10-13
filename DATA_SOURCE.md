# 데이터 수집 안내

이 저장소는 통계 원본 파일의 라이선스 확인 전까지 원본 CSV/XLS/XLSX 파일을 Git에 포함하지 않는다. 따라서 재현을 위해서는 아래 안내에 따라 사용자가 직접 원본 데이터를 내려받아 `data/raw/` 폴더에 저장해야 한다.

## 1. 폴더 위치

원본 데이터 파일은 다음 위치에 둔다.

```text
data/raw/
```

전처리 결과는 다음 위치에 생성된다.

```text
data/processed/
```

주의: `data/raw/*.csv`, `data/raw/*.xls`, `data/raw/*.xlsx`, `data/processed/*.csv` 등은 `.gitignore`에 의해 Git에 올라가지 않는다.

## 2. 서비스업생산지수 데이터

### 출처

- 기관: 통계청 KOSIS
- 통계: 서비스업동향조사 / 서비스업생산지수
- 주기: 월
- 기간: 2017.01 ~ 2026.08 또는 가능한 최신 월까지

### 검색어 예시

KOSIS에서 다음 키워드로 검색한다.

```text
서비스업생산지수
```

또는

```text
산업별 서비스업생산지수
```

### 선택 조건

| 항목 | 선택 |
|---|---|
| 주기 | 월 |
| 기간 | 2017.01 ~ 2026.08 또는 최신 |
| 업종 | 정보통신업, 소프트웨어 개발 및 공급업, 컴퓨터 프로그래밍·시스템 통합 및 관리업, 정보서비스업 |
| 지표 | 경상지수, 불변지수, 계절조정지수 |

분석의 기본 지표는 `불변지수`이다. `경상지수`는 비교 그래프에 사용하고, `계절조정지수`는 필요 시 장기 추세 보조 지표로 사용한다.

### 저장 파일 예시

다운로드한 CSV 파일을 `data/raw/`에 저장한다.

예시:

```text
data/raw/101_DT_1KC2020_YYYYMMDDHHMMSS.csv
```

전처리 스크립트는 `data/raw/`에서 다음 조건을 만족하는 CSV를 자동으로 찾는다.

- `업종별`, `항목` 컬럼 포함
- `2017.01 월` 같은 월별 컬럼 100개 이상 포함
- cp949 인코딩으로 읽을 수 있음

## 3. 직종별 구인구직취업현황 데이터

### 출처

- 기관: 한국고용정보원 고용행정통계
- 통계: 직종별 구인구직취업현황(월)
- 지역: 전체
- 주기: 월

### 사이트

```text
https://eis.work.go.kr
```

### 검색어 예시

```text
직종별 구인구직취업현황
```

또는

```text
직종별 구인구직
```

### 선택 조건

| 항목 | 선택 |
|---|---|
| 주기 | 월 |
| 지역 | 전체 |
| 기간 1 | 2017.01 ~ 2021.09 |
| 기간 2 | 2021.09 ~ 2026.08 또는 최신 |
| 지표 | 구인인원(월), 구직건수(월), 취업건수(월) |
| 직종 | 전체 직종 또는 정보통신 관련 직종 포함 |

기간을 두 개로 나눈 이유는 직종분류 개정으로 인해 한 번에 모든 기간을 내려받기 어려울 수 있기 때문이다. 본 프로젝트에서는 다음 두 파일을 사용했다.

```text
data/raw/직종별_구인구직취업현황(월)_1791901933253.xlsx
data/raw/직종별_구인구직취업현황(월)_1791899901678.xls
```

파일명은 달라도 된다. 단, `직종별_구인구직취업현황`으로 시작하는 xls/xlsx 파일이면 전처리 스크립트가 자동으로 읽는다.

## 4. 직종 연결 기준

직종분류가 2007, 2018, 2025 체계로 바뀌었기 때문에, 분석에서는 다음처럼 유사 직종을 연결한다.

| 분석 지표 | 연결 대상 |
|---|---|
| it_broad | 2007직종_정보통신 관련직 전체 |
| it_broad | 2018직종_정보통신 연구개발직 및 공학기술직 전체 |
| it_broad | 2025직종_정보통신 연구개발직 및 공학기술직 전체 |
| software_developer | 2007직종_소프트웨어개발전문가 |
| software_developer | 2018직종_소프트웨어 개발자 |
| software_developer | 2025직종_소프트웨어 개발자 |

주의: 이 연결은 분석을 위한 매핑이며, 각 직종분류가 완전히 동일한 정의라는 의미는 아니다.

## 5. 전처리 실행

원본 파일을 `data/raw/`에 넣은 뒤 다음 명령을 실행한다.

```zsh
python3 src/preprocess.py
```

성공 시 다음 파일이 생성된다.

```text
data/processed/service_production_long.csv
data/processed/job_demand_long.csv
data/processed/merged_monthly.csv
```

## 6. 분석 실행

전처리 후 다음 명령을 실행한다.

```zsh
python3 src/analyze.py
```

성공 시 다음 이미지와 요약 파일이 생성된다.

```text
images/01_service_trend_constant_index.png
images/02_monthly_seasonality_by_industry.png
images/03_current_vs_constant_index.png
images/04_service_vs_job_demand_indexed.png
images/05_seasonal_naive_forecast_error.png
images/06_lag_correlation_service_vs_jobs.png
data/processed/analysis_metrics.md
```
