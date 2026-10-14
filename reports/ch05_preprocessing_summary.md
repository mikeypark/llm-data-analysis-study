# Chapter 5 데이터 전처리 요약

## 전처리 결과 파일

customers_clean.csv / products_clean.csv / orders_clean.csv / order_items_clean.csv

## 전처리 전후 데이터 크기

```text
    dataset  rows_raw  columns_raw  rows_processed  columns_processed
  customers       150            6             150                  6
   products       100            4             100                  4
     orders       300            5             300                  7
order_items       764            5             764                  6
```

## 파일 간 관계 점검 결과

```text
                                               check  invalid_count
  orders.customer_id exists in customers.customer_id              0
      order_items.order_id exists in orders.order_id              0
order_items.product_id exists in products.product_id              0
```

## 주요 처리 내용

원본 데이터를 직접 수정하지 않고 복사본을 사용했다. 결측치 0건(샘플 기준), age 중앙값(40.0) 대체 로직 구성. 전체 행 중복 0건, 주요 ID 중복 0건. 문자열 앞뒤 공백 제거(변화 없음). 주문 상태값 표기 통일 맵 적용(변화 없음). order_date, signup_date 날짜형 변환(실패 0건). order_month, order_dayofweek 파생 컬럼 생성. price, quantity, unit_price 숫자형 변환(실패 0건). 0 이하 이상값 0건 확인 및 처리 기준 적용. line_total = quantity × unit_price 파생 컬럼 생성. 파일 간 키 관계 재확인(invalid 0건).

## 주의 사항

이 전처리 기준은 실습용 예시다. 실데이터에서는 결측치·이상값 처리 전에 원본 시스템과 업무 담당자 확인이 필요하다.
