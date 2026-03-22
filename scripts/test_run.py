import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = REPO_ROOT / "data" / "input" / "sales_data_sample.csv"

def main():
    df = pd.read_csv(INPUT_FILE, encoding='cp1252')
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
    total_sales = df[df['ORDERDATE'] > '2005-01-01']['SALES'].sum()
    print(f'Total sales after January 2, 2004: {total_sales}')
    return total_sales

if __name__ == '__main__':
    main()