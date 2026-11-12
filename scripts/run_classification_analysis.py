"""
chapter10 분류 분석 재실행 스크립트
- Notebook과 동일한 타깃/분할/전처리/평가 원칙 사용
- 실행: python scripts/run_classification_analysis.py
"""

from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'

def main():
    # 데이터 로드
    customers = pd.read_csv(PROCESSED_DIR / 'customers_clean.csv')
    orders    = pd.read_csv(PROCESSED_DIR / 'orders_clean.csv')

    orders['order_date']     = pd.to_datetime(orders['order_date'], errors='coerce')
    orders['order_month']    = orders['order_date'].dt.to_period('M').astype(str)
    orders['order_dayofweek']= orders['order_date'].dt.dayofweek
    orders['is_cancelled']   = (orders['order_status'] == 'cancelled').astype(int)

    model_data = (
        orders
        .merge(customers[['customer_id', 'gender', 'age', 'city']], on='customer_id', how='left')
        .sort_values('order_date')
        .reset_index(drop=True)
    )

    NUM  = ['order_dayofweek', 'age']
    CAT  = ['payment_method', 'order_month', 'gender', 'city']
    FEAT = NUM + CAT
    TARGET = 'is_cancelled'

    n = len(model_data)
    train_data = model_data.iloc[:int(n * 0.8)]
    val_data   = model_data.iloc[int(n * 0.8):int(n * 0.9)]
    test_data  = model_data.iloc[int(n * 0.9):]

    X_train, y_train = train_data[FEAT], train_data[TARGET]
    X_val,   y_val   = val_data[FEAT],   val_data[TARGET]
    X_test,  y_test  = test_data[FEAT],  test_data[TARGET]

    # 전처리 파이프라인
    num_pipe = Pipeline([('imp', SimpleImputer(strategy='median')), ('sc', StandardScaler())])
    cat_pipe = Pipeline([('imp', SimpleImputer(strategy='most_frequent')),
                         ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    preprocessor = ColumnTransformer([
        ('num', num_pipe, NUM),
        ('cat', cat_pipe, CAT),
    ])

    # Dummy Classifier
    dummy = DummyClassifier(strategy='most_frequent', random_state=42)
    dummy.fit(X_train, y_train)

    # LogisticRegression
    lr = Pipeline([('pre', preprocessor), ('m', LogisticRegression(max_iter=1000, random_state=42))])
    lr.fit(X_train, y_train)
    y_lr_prob_val  = lr.predict_proba(X_val)[:, 1]
    y_lr_prob_test = lr.predict_proba(X_test)[:, 1]
    THRESHOLD = 0.20

    y_lr_val  = (y_lr_prob_val  >= THRESHOLD).astype(int)
    y_lr_test = (y_lr_prob_test >= THRESHOLD).astype(int)

    def report(name, y_true, y_pred):
        return {
            'model':     name,
            'Accuracy':  round(accuracy_score(y_true, y_pred), 4),
            'Precision': round(precision_score(y_true, y_pred, zero_division=0), 4),
            'Recall':    round(recall_score(y_true, y_pred, zero_division=0), 4),
            'F1':        round(f1_score(y_true, y_pred, zero_division=0), 4),
        }

    print('=' * 60)
    print('Chapter 10 - 주문 취소 분류 분석 재실행 결과')
    print('=' * 60)
    print(f'데이터: train={len(train_data)}, val={len(val_data)}, test={len(test_data)}')
    print(f'타깃(is_cancelled) - train: {int(y_train.sum())}건, val: {int(y_val.sum())}건, test: {int(y_test.sum())}건')
    print(f'사용 Threshold: {THRESHOLD}')
    print()

    rows = [
        report('Dummy (most_frequent)',           y_val, dummy.predict(X_val)),
        report(f'LR (thresh={THRESHOLD})',        y_val, y_lr_val),
    ]
    print('[Validation]')
    for r in rows:
        print(f"  {r['model']:40s} Acc={r['Accuracy']:.4f}  P={r['Precision']:.4f}  R={r['Recall']:.4f}  F1={r['F1']:.4f}")

    print()
    print('[Confusion Matrix - LR (validation, thresh=0.20)]')
    cm_val = confusion_matrix(y_val, y_lr_val)
    print(f'  TN={cm_val[0,0]}, FP={cm_val[0,1]}, FN={cm_val[1,0]}, TP={cm_val[1,1]}')

    rows_test = [
        report('Dummy (most_frequent)',           y_test, dummy.predict(X_test)),
        report(f'LR (thresh={THRESHOLD})',        y_test, y_lr_test),
    ]
    print()
    print('[Final Test]')
    for r in rows_test:
        print(f"  {r['model']:40s} Acc={r['Accuracy']:.4f}  P={r['Precision']:.4f}  R={r['Recall']:.4f}  F1={r['F1']:.4f}")

    print()
    print('[Confusion Matrix - LR (final test, thresh=0.20)]')
    cm_test = confusion_matrix(y_test, y_lr_test)
    print(f'  TN={cm_test[0,0]}, FP={cm_test[0,1]}, FN={cm_test[1,0]}, TP={cm_test[1,1]}')
    print()
    print('완료')

if __name__ == '__main__':
    main()
