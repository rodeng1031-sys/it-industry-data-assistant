# Analysis Metrics

## Data coverage
- Service production index: 2017-01-01 ~ 2026-08-01, rows=1392
- Job demand: 2017-01-01 ~ 2026-08-01, rows=232
- Merged monthly table: 2017-01-01 ~ 2026-08-01, rows=116

## Q1. March concentration, SI-related industry
- March average seasonal ratio: 94.92
- Non-March average seasonal ratio: 100.48

## Q2. Long-term trend and COVID reference period
- First value (2017-01-01): 69.7
- Last value (2026-08-01): 128.1
- Change from first to last: 83.8%
- Lowest value in 2020-02~2021-12: 80.6 at 2021-01-01

## Q3. Seasonality difference by industry
- Programming, SI & management: seasonal-ratio std=29.58
- Software development & supply: seasonal-ratio std=15.54
- Information & communication: seasonal-ratio std=12.19
- Information services: seasonal-ratio std=10.79

## Q4. Correlation, service index vs job openings
- Same-month corr(service, broad IT openings): -0.319
- Same-month corr(service, software developer openings): -0.292
- Lag correlation convention: negative lag = job demand leads, positive lag = service activity leads
- Best positive correlation for broad_it: lag=-2, corr=-0.132, n=114
- Strongest negative correlation for broad_it: lag=0, corr=-0.319, n=116
- Best positive correlation for software_developer: lag=-2, corr=-0.081, n=114
- Strongest negative correlation for software_developer: lag=0, corr=-0.292, n=116

## Q5. Seasonal naive forecast errors
- Worst 5 months across evaluable period:
  - 2024-12-01: actual=222.7, forecast=262.4, APE=17.8%
  - 2026-05-01: actual=129.7, forecast=109.2, APE=15.8%
  - 2023-06-01: actual=139.9, forecast=118.4, APE=15.4%
  - 2018-11-01: actual=97.7, forecast=112.0, APE=14.6%
  - 2023-08-01: actual=117.8, forecast=100.7, APE=14.5%
- Worst 3 months in the last 12 months:
  - 2026-05-01: actual=129.7, forecast=109.2, APE=15.8%
  - 2025-09-01: actual=138.0, forecast=118.1, APE=14.4%
  - 2026-07-01: actual=136.0, forecast=123.0, APE=9.6%
