import pandas as pd

def main():
    df = pd.read_csv('sales_data_sample.csv', encoding='cp1252')
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
    total_sales = df[df['ORDERDATE'] > '2004-01-01']['SALES'].sum()
    print(f'Total sales after January 2, 2004: {total_sales}')
    return total_sales

if __name__ == '__main__':
    main()