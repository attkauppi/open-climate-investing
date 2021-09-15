import argparse
import pandas as pd
import stock_price_function as spf
import input_function
import db


csv_file = 'stock_tickers.csv'

conn = db.get_db_connection()


def load_stocks_csv(filename):
    print('Loading stock tickers CSV {} ...'.format(filename))
    all_stock_data = pd.read_csv(filename, header=None)
    return all_stock_data.values


def import_stock(stock_name):
    stock_data = load_stocks_data(stock_name)
    import_stocks_into_db(stock_name, stock_data)
    return stock_data


def load_stocks_data(stock_name):
    stock_data = spf.stock_df_grab(stock_name)
    stock_data = input_function.convert_to_form(stock_data)
    return stock_data


def import_stocks_into_db(stock_name, stock_data):
    sql = '''INSERT INTO
        stock_data (ticker, date, close)
        VALUES (%s, %s, %s)
        ON CONFLICT (ticker, date) DO
        UPDATE SET close = EXCLUDED.close;'''
    with conn.cursor() as cursor:
        for index, row in stock_data.iterrows():
            print('-- {} = {}'.format(index, row['Close']))
            cursor.execute(sql, (stock_name, index, row['Close']))


def load_stocks_from_db(stock_name):
    sql = '''SELECT date, close
        FROM stock_data
        WHERE ticker = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='date', params=(stock_name,))


def main(args):
    if args.ticker:
        import_stock(args.ticker)
    elif args.show:
        df = load_stocks_from_db(args.show)
        print('Loaded from DB: {} entries'.format(len(df)))
        print(' -- sample (truncated) -- ')
        print(df)
    else:
        stocks = load_stocks_csv(args.file)

        for i in range(0, len(stocks)):
            stock_name = stocks[i].item()
            import_stock(stock_name)


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default=csv_file,
                        help="specify the CSV file of stock tickers to import")
    parser.add_argument("-t", "--ticker",
                        help="specify a single ticker to import, ignores the CSV file")
    parser.add_argument("-s", "--show",
                        help="Show the data for a given ticker, for testing")
    main(parser.parse_args())