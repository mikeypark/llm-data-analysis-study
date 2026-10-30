"""
8장 중간 프로젝트 일괄 실행 스크립트.
프로젝트 루트에서 실행: python scripts/run_midterm_project.py
"""

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
REPORT_DIR = PROJECT_ROOT / 'reports'
FIGURE_DIR = REPORT_DIR / 'figures'
REPORT_DIR.mkdir(exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

print('프로젝트 루트:', PROJECT_ROOT)
print('전처리 데이터 폴더:', PROCESSED_DIR)

# ── 데이터 로드 ──────────────────────────────────────────────────────────────
customers = pd.read_csv(PROCESSED_DIR / 'customers_clean.csv')
products  = pd.read_csv(PROCESSED_DIR / 'products_clean.csv')
orders    = pd.read_csv(PROCESSED_DIR / 'orders_clean.csv')
order_items = pd.read_csv(PROCESSED_DIR / 'order_items_clean.csv')

orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
if 'order_month' not in orders.columns:
    orders['order_month'] = orders['order_date'].dt.to_period('M').astype(str)
if 'line_total' not in order_items.columns:
    order_items['line_total'] = order_items['quantity'] * order_items['unit_price']

print('데이터 로드 완료')

# ── PK 중복 검증 ──────────────────────────────────────────────────────────────
pk_checks = {
    'customers.customer_id': customers['customer_id'].duplicated().sum(),
    'products.product_id': products['product_id'].duplicated().sum(),
    'orders.order_id': orders['order_id'].duplicated().sum(),
    'order_items.order_item_id': order_items['order_item_id'].duplicated().sum(),
}
for k, v in pk_checks.items():
    print(f'PK 중복 {k}: {v}')

# ── completed 집계 ────────────────────────────────────────────────────────────
order_sales = order_items.merge(
    orders[['order_id', 'customer_id', 'order_date', 'order_month', 'order_status']],
    on='order_id', how='left', validate='many_to_one',
)
completed = order_sales[order_sales['order_status'] == 'completed'].copy()
completed_items = completed.merge(
    products, on='product_id', how='left', validate='many_to_one',
)

completed_total = completed['line_total'].sum()
print(f'completed 원본 합계: {completed_total:,.0f}원')

category_sales = (
    completed_items
    .groupby('category', as_index=False)
    .agg(total_quantity=('quantity', 'sum'), total_sales=('line_total', 'sum'))
    .sort_values('total_sales', ascending=False)
)
category_sales['sales_ratio'] = (
    category_sales['total_sales'] / category_sales['total_sales'].sum() * 100
).round(2)

monthly_sales = (
    completed
    .groupby('order_month', as_index=False)
    .agg(total_sales=('line_total', 'sum'), order_count=('order_id', 'nunique'))
    .sort_values('order_month')
)

customer_sales = (
    completed
    .groupby('customer_id', as_index=False)
    .agg(order_count=('order_id', 'nunique'), total_sales=('line_total', 'sum'))
    .sort_values('total_sales', ascending=False)
)
customer_sales = customer_sales.merge(
    customers[['customer_id', 'city']], on='customer_id', how='left',
)
customer_sales['avg_order_value'] = (
    customer_sales['total_sales'] / customer_sales['order_count']
).round(0)
customer_sales['customer_label'] = 'Customer ' + customer_sales['customer_id'].astype(str)

# ── 합계 검증 ──────────────────────────────────────────────────────────────────
assert category_sales['total_sales'].sum() == completed_total
assert monthly_sales['total_sales'].sum() == completed_total
assert customer_sales['total_sales'].sum() == completed_total
print('집계 합계 검증 통과')

# ── CSV 저장 ──────────────────────────────────────────────────────────────────
category_sales.to_csv(REPORT_DIR / 'ch08_category_sales.csv', index=False, encoding='utf-8-sig')
monthly_sales.to_csv(REPORT_DIR / 'ch08_monthly_sales.csv', index=False, encoding='utf-8-sig')
customer_sales.to_csv(REPORT_DIR / 'ch08_customer_sales.csv', index=False, encoding='utf-8-sig')
print('CSV 저장 완료')

# ── 그래프 저장 ───────────────────────────────────────────────────────────────
# graph01: 카테고리별 completed 매출
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(category_sales['category'], category_sales['total_sales'],
              color='steelblue', edgecolor='white')
for bar, ratio in zip(bars, category_sales['sales_ratio']):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200_000,
            f'{ratio}%', ha='center', va='bottom', fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1_000_000:.0f}백만'))
ax.set_title('카테고리별 completed 매출 (2025-07 ~ 2026-07)', fontsize=13)
ax.set_xlabel('카테고리', fontsize=11)
ax.set_ylabel('completed 매출 (백만 원)', fontsize=11)
ax.set_ylim(0, category_sales['total_sales'].max() * 1.15)
plt.tight_layout()
plt.savefig(FIGURE_DIR / 'ch08_category_sales.png', dpi=150, bbox_inches='tight')
plt.close()

# graph02: 월별 completed 매출
fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(monthly_sales['order_month'], monthly_sales['total_sales'],
         marker='o', color='steelblue', linewidth=2, label='completed 매출')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1_000_000:.0f}백만'))
ax1.set_ylabel('completed 매출 (백만 원)', fontsize=11, color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')
ax2 = ax1.twinx()
ax2.bar(monthly_sales['order_month'], monthly_sales['order_count'],
        alpha=0.25, color='gray', label='주문 수')
ax2.set_ylabel('주문 수 (건)', fontsize=11, color='gray')
ax2.tick_params(axis='y', labelcolor='gray')
ax1.set_title('월별 completed 매출 및 주문 수 (2025-07 ~ 2026-07)', fontsize=13)
ax1.set_xlabel('주문 월', fontsize=11)
plt.xticks(rotation=45)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.tight_layout()
plt.savefig(FIGURE_DIR / 'ch08_monthly_sales.png', dpi=150, bbox_inches='tight')
plt.close()

# graph03: 상위 10 고객
top10 = customer_sales.head(10).sort_values('total_sales')
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top10['customer_label'], top10['total_sales'], color='steelblue', edgecolor='white')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1_000_000:.1f}백만'))
ax.set_title('completed 구매 금액 상위 10명 고객', fontsize=13)
ax.set_xlabel('총 구매 금액 (백만 원)', fontsize=11)
ax.set_ylabel('고객', fontsize=11)
plt.tight_layout()
plt.savefig(FIGURE_DIR / 'ch08_top_customers.png', dpi=150, bbox_inches='tight')
plt.close()

print('그래프 저장 완료:')
for p in sorted(FIGURE_DIR.glob('ch08_*.png')):
    print(' ', p.name, p.stat().st_size, 'bytes')

print('\n=== 핵심 수치 요약 ===')
print(f'completed 원본 합계: {completed_total:,.0f}원')
print(f'카테고리 1위: {category_sales.iloc[0]["category"]} {category_sales.iloc[0]["total_sales"]:,.0f}원 ({category_sales.iloc[0]["sales_ratio"]}%)')
print(f'월별 피크: {monthly_sales.loc[monthly_sales["total_sales"].idxmax(), "order_month"]} {monthly_sales["total_sales"].max():,.0f}원')
print(f'구매 금액 1위 고객: {customer_sales.iloc[0]["customer_label"]} {customer_sales.iloc[0]["total_sales"]:,.0f}원')
print('\nrun_midterm_project.py 완료')
