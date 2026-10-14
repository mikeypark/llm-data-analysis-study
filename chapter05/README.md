# Chapter 05. 분석을 믿을 수 있게 만드는 데이터 전처리

## 제출 정보

이름: 박성주 / GitHub ID: mikeypark / 작성일: 2026-10-14

## 실습 목표

원본 데이터를 복사해 전처리 전후를 비교하고, 결측치·중복·이상값 처리 기준을 기록한다. 날짜형·숫자형 변환과 파생 컬럼 생성 후 파일 간 키 관계를 재확인하고, 결과를 `data/processed/`와 요약 보고서로 저장한다.

## 제출 파일

| 파일 | 설명 |
|------|------|
| `chapter05/chapter05.ipynb` | 실행 완료 노트북 (주 제출물) |
| `data/processed/customers_clean.csv` | 전처리된 고객 데이터 |
| `data/processed/products_clean.csv` | 전처리된 상품 데이터 |
| `data/processed/orders_clean.csv` | 전처리된 주문 데이터 |
| `data/processed/order_items_clean.csv` | 전처리된 주문 상세 데이터 |
| `reports/ch05_preprocessing_summary.md` | 전처리 요약 보고서 |

## 전처리 전후 요약

| 데이터셋 | 행(전) | 열(전) | 행(후) | 열(후) | 주요 변경 |
|----------|--------|--------|--------|--------|----------|
| customers | 150 | 6 | 150 | 6 | age 중앙값 대체 로직 구성 |
| products | 100 | 4 | 100 | 4 | price 숫자형 변환 |
| orders | 300 | 5 | 300 | 7 | +order_month, +order_dayofweek |
| order_items | 764 | 5 | 764 | 6 | +line_total |

## 주요 확인 결과

| 항목 | 결과 |
|------|------|
| 결측치 | 모든 데이터셋 0건 |
| 중복 | 전체 행 중복 0건, 주요 ID 중복 0건 |
| 이상값(price/quantity/unit_price ≤ 0) | 0건 |
| 날짜 변환 실패 | 0건 |
| 파일 간 키 관계 이상 | 0건 |
