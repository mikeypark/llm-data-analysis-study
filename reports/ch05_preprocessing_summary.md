# Chapter 5 데이터 전처리 요약

## 전처리 결과 파일
- customers_clean.csv
- products_clean.csv
- orders_clean.csv
- order_items_clean.csv

## 전처리 전후 데이터 크기
| 데이터셋 | 행(전) | 열(전) | 행(후) | 열(후) |
|---------|--------|--------|--------|--------|
| customers | 150 | 6 | 150 | 6 |
| products | 100 | 4 | 100 | 4 |
| orders | 300 | 5 | 300 | 7 |
| order_items | 764 | 5 | 764 | 6 |

## 파일 간 관계 점검
- orders.customer_id 무효: 0건
- order_items.order_id 무효: 0건
- order_items.product_id 무효: 0건

## 주요 처리 내용
- 원본 복사본 사용 (원본 보호)
- 결측치 0건 확인, age 중앙값(40.0) 대체 로직 구성
- 전체 행 중복 0건, 주요 ID 중복 0건
- 문자열 앞뒤 공백 제거, 주문 상태값 표기 통일
- order_date, signup_date 날짜형 변환 (실패 0건)
- order_month, order_dayofweek 파생 컬럼 생성
- price, quantity, unit_price 숫자형 변환 (실패 0건)
- 0 이하 이상값 0건 확인
- line_total = quantity x unit_price 파생 컬럼 생성
- 파일 간 키 관계 재확인 (무효 0건)
