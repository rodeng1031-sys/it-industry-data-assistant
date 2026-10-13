# 컬럼 매핑

## 1. KOSIS 서비스업생산지수

출처: KOSIS / 통계청, 서비스업동향조사 서비스업생산지수

| 원본 컬럼/값 | 분석용 컬럼/값 | 설명 |
|---|---|---|
| 업종별 | industry_ko | 원본 업종명 |
| 정보통신업 | information_communication | IT/정보통신업 전체 후보 |
| 소프트웨어 개발 및 공급업 | software_development_supply | SW 업종 |
| 컴퓨터 프로그래밍, 시스템 통합 및 관리업 | computer_programming_system_integration | SI/시스템 통합 관련 업종 |
| 정보서비스업 | information_service | 정보서비스 관련 업종 |
| 항목 | index_type_ko | 원본 지수 종류 |
| 경상지수 | current_index | 명목 흐름에 가까운 지수, 비교 그래프용 |
| 불변지수 | constant_index | 기본 분석 지표 |
| 계절조정지수 | seasonally_adjusted_index | 장기 추세 보조 지표 |
| 2017.01 월 등 | date | 월 단위 날짜 |
| 값 | value | 생산지수 값 |

## 2. 고용행정통계 직종별 구인구직취업현황

출처: 한국고용정보원 고용행정통계, 직종별 구인구직취업현황(월)

| 원본 컬럼/값 | 분석용 컬럼/값 | 설명 |
|---|---|---|
| 마감년월 | date | 월 단위 날짜 |
| 직종_중분류 | occupation_middle | 원본 중분류 직종 |
| 직종_소분류 | occupation_small | 원본 소분류 직종 |
| 구인인원(월) | job_openings | 월별 구인인원 |
| 구직건수(월) | job_seekers | 월별 구직건수 |
| 취업건수(월) | placements | 월별 취업건수 |
| 구인인원(월) / 구직건수(월) | opening_to_seeker_ratio | 분석용 구인/구직 비율. 공식 구인배율은 아님 |

## 3. 구인 수요 지표 연결 기준

직종분류 개정이 있으므로 분석용 지표를 다음처럼 연결한다.

| 분석 지표 | 연결 대상 |
|---|---|
| it_broad | 2007직종_정보통신 관련직 전체 |
| it_broad | 2018직종_정보통신 연구개발직 및 공학기술직 전체 |
| it_broad | 2025직종_정보통신 연구개발직 및 공학기술직 전체 |
| software_developer | 2007직종_소프트웨어개발전문가 |
| software_developer | 2018직종_소프트웨어 개발자 |
| software_developer | 2025직종_소프트웨어 개발자 |

주의: 2007/2018/2025 직종분류는 완전히 동일한 정의가 아닐 수 있으므로 분류 전환 시점의 변화는 해석에 주의한다.
