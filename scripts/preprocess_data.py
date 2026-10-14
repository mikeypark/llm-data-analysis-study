"""
Chapter 05 데이터 전처리 스크립트.
프로젝트 루트에서 실행:
    python scripts/preprocess_data.py
"""

from pathlib import Path

import pandas as pd
import numpy as np


def find_project_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "requirements.txt").exists() and (candidate / "scripts").exists():
            return candidate
    raise FileNotFoundError("프로젝트 루트를 찾을 수 없습니다.")


PROJECT_ROOT = find_project_root(Path(__file__).resolve().parent)
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

STATUS_MAP = {
    "complete": "completed", "Complete": "completed",
    "COMPLETED": "completed", "완료": "completed",
    "cancel": "cancelled", "Cancel": "cancelled",
    "CANCELLED": "cancelled", "취소": "cancelled",
    "refund": "refunded", "Refund": "refunded",
    "REFUNDED": "refunded", "환불": "refunded",
}


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for col in result.select_dtypes(include=["object", "str"]).columns:
        result[col] = result[col].where(
            result[col].isna(),
            result[col].astype(str).str.strip(),
        )
    return result


def _to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )


def preprocess_customers(df: pd.DataFrame) -> pd.DataFrame:
    result = _strip_strings(df.drop_duplicates())
    result["age"] = pd.to_numeric(result["age"], errors="coerce")
    result["age"] = result["age"].fillna(result["age"].median())
    result["city"] = result["city"].fillna("Unknown")
    if "signup_date" in result.columns:
        result["signup_date"] = pd.to_datetime(result["signup_date"], errors="coerce")
    return result


def preprocess_products(df: pd.DataFrame) -> pd.DataFrame:
    result = _strip_strings(df.drop_duplicates())
    result["price"] = _to_number(result["price"])
    return result[result["price"] > 0].copy()


def preprocess_orders(df: pd.DataFrame) -> pd.DataFrame:
    result = _strip_strings(df.drop_duplicates())
    if "order_status" in result.columns:
        result["order_status"] = result["order_status"].replace(STATUS_MAP)
    if "order_date" in result.columns:
        result["order_date"] = pd.to_datetime(result["order_date"], errors="coerce")
        result["order_month"] = result["order_date"].dt.to_period("M").astype(str)
        result["order_dayofweek"] = result["order_date"].dt.day_name()
    return result


def preprocess_order_items(df: pd.DataFrame) -> pd.DataFrame:
    result = _strip_strings(df.drop_duplicates())
    result["quantity"] = _to_number(result["quantity"])
    result["unit_price"] = _to_number(result["unit_price"])
    result = result[(result["quantity"] > 0) & (result["unit_price"] > 0)].copy()
    result["line_total"] = result["quantity"] * result["unit_price"]
    return result


def main() -> None:
    print("=== Chapter 05 전처리 스크립트 시작 ===")

    customers = pd.read_csv(RAW_DIR / "customers.csv")
    products = pd.read_csv(RAW_DIR / "products.csv")
    orders = pd.read_csv(RAW_DIR / "orders.csv")
    order_items = pd.read_csv(RAW_DIR / "order_items.csv")

    raw_shapes = {
        "customers": customers.shape,
        "products": products.shape,
        "orders": orders.shape,
        "order_items": order_items.shape,
    }

    customers_clean = preprocess_customers(customers)
    products_clean = preprocess_products(products)
    orders_clean = preprocess_orders(orders)
    order_items_clean = preprocess_order_items(order_items)

    processed = {
        "customers": customers_clean,
        "products": products_clean,
        "orders": orders_clean,
        "order_items": order_items_clean,
    }

    for name, df in processed.items():
        path = PROCESSED_DIR / f"{name}_clean.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        raw_r, raw_c = raw_shapes[name]
        print(
            f"  {name}: ({raw_r},{raw_c}) -> {df.shape}"
            f"  saved: {path.name} ({path.stat().st_size} bytes)"
        )

    relationship_issues = {
        "orders.customer_id": len(
            orders_clean[~orders_clean["customer_id"].isin(customers_clean["customer_id"])]
        ),
        "order_items.order_id": len(
            order_items_clean[~order_items_clean["order_id"].isin(orders_clean["order_id"])]
        ),
        "order_items.product_id": len(
            order_items_clean[~order_items_clean["product_id"].isin(products_clean["product_id"])]
        ),
    }

    print("\n파일 간 관계 점검:")
    for check, count in relationship_issues.items():
        status = "PASS" if count == 0 else f"FAIL ({count}건)"
        print(f"  {check}: {status}")

    print(f"\n보고서: {REPORT_DIR / 'ch05_preprocessing_summary.md'}")
    print("=== 전처리 완료 ===")


if __name__ == "__main__":
    main()
