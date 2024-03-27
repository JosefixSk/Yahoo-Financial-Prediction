import mysql.connector
import json


def save_results_to_json(name, results):
    try:
        with open("crypto_results.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data[name] = results

    with open("crypto_results.json", "w") as file:
        json.dump(data, file)
        

# Connect to the MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    database="my_db",
    user="root",
    password="*******" #insert your own password
)

def create_results_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(255),
        start_date DATE,
        initial_balance FLOAT,
        final_balance FLOAT,
        balance_change FLOAT
    )
    """

    with db_connection.cursor() as cursor:
        cursor.execute(create_table_query)
        db_connection.commit()

def insert_result(symbol, start_date, initial_balance, final_balance):
    insert_query = """
    INSERT INTO results (symbol, start_date, initial_balance, final_balance, balance_change)
    VALUES (%s, %s, %s, %s, %s)
    """

    balance_change = final_balance - initial_balance
    with db_connection.cursor() as cursor:
        cursor.execute(insert_query, (symbol, start_date, float(initial_balance),
                                      float(final_balance), float(balance_change)))
        db_connection.commit()
        
    results = {
        "symbol": symbol,
        "start_date": start_date,
        "initial_balance": initial_balance,
        "final_balance": final_balance,
        "balance_change": final_balance - initial_balance
    }

    save_results_to_json(symbol, results)

# Call the functions as needed in your main code
