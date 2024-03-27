import json
from database import save_results_to_json
import yfinance as yf
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import database
from database import create_results_table, insert_result
import mysql.connector

matplotlib.use("TkAgg")  # Add this line to set the backend

# Dictionary to hold user-specific results
user_results = {}

def plot_candlestick(symbol, start_date, end_date):
    # Retrieve data using yfinance
    data = yf.download(symbol, start=start_date, end=end_date)

    if data.empty:
        print(f"No data available for symbol '{symbol}' during the specified period.")
        return

    # Convert index to DatetimeIndex
    data.index = pd.to_datetime(data.index)

    # Create a candlestick chart
    fig, _ = mpf.plot(data, type='candle', title=f"{symbol} Candlestick Chart", ylabel='Price', 
                      returnfig=True)
      
    return fig

def plot_daily_returns(symbol, start_date, end_date):
    stock = yf.Ticker(symbol)
    historical_data = stock.history(start=start_date, end=end_date)
    daily_returns = historical_data['Close'].pct_change()
    
    
    # Create and train a linear regression model
    model = LinearRegression()
    daily_returns = daily_returns.dropna()
    X = pd.to_numeric(daily_returns.index.values).reshape(-1, 1)
    y = daily_returns.values
    model.fit(X, y)

    # Make predictions using the trained model
    y_pred = model.predict(X)
    
    # Create a figure for daily returns and regression line
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(daily_returns.index, daily_returns, label='Daily Returns')
    ax1.plot(daily_returns.index, y_pred, color='r', label='Linear Regression')
    ax1.axhline(y=0, color='r', linestyle='--', label='Zero Line')
    ax1.set_title(f'Daily Returns and Linear Regression for {symbol}  Stock')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Percentage Change')
    ax1.legend()
    
    # Create a figure for daily returns without regression line
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.plot(daily_returns.index, daily_returns, label='Daily Returns')
    ax2.axhline(y=0, color='r', linestyle='--', label='Zero Line')
    ax2.set_title(f'Daily Returns for {symbol} Stock')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Percentage Change')
    ax2.legend()
    # Return both figures
    return fig1, fig2
    


def on_submit():
    username = username_entry.get()  # Assign the entered name to specific_name
    balance = balance_entry.get()
    symbol = symbol_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    
    
    # Validate the balance input
    try:
        balance = float(balance)
        if balance < 100 or balance > 100000:
            raise ValueError("Balance must be between 100 and 100000")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
    
    # Calculate the change in balance based on daily returns
    stock = yf.Ticker(symbol)
    historical_data = stock.history(start=start_date, end=end_date)
    daily_returns = historical_data['Close'].pct_change().dropna()
    
    if daily_returns.empty:
        messagebox.showinfo("Info", "No data available for the specified period.")
        return
    
    final_balance = balance * (1 + daily_returns.sum())
    # Store the results in the user_results dictionary
    user_results[username] = {
        "symbol": symbol,
        "start_date": start_date,
        "initial_balance": balance,
        "final_balance": final_balance,
        "balance_change": final_balance - balance
    }
    save_results_to_json(username, user_results)
    
    messagebox.showinfo("Balance Change", f"Initial Balance: ${balance:.2f}\n"
                                          f"Change in Balance: ${(final_balance - balance):.2f}\n"
                                          f"Final Balance: ${final_balance:.2f}")

    # Get the figures
    candlestick_fig = plot_candlestick(symbol, start_date, end_date)
    daily_returns_figs = plot_daily_returns(symbol, start_date, end_date)
    
    # Insert the result into the database
    create_results_table()
    insert_result(symbol, start_date, balance, final_balance)
    
    # Display the figures in separate windows
    if candlestick_fig is not None:
        plt.figure(candlestick_fig.number)
        plt.show()
    
    if daily_returns_figs is not None:
        for fig in daily_returns_figs:
            plt.figure(fig.number)
            plt.show()
            
    
    
    

# Create the main application window
root = tk.Tk()
root.title("Crypto Trading Data Science Project")

# Create and place input fields and labels for username
username_label = ttk.Label(root, text="Enter your username:")
username_label.pack()
username_entry = ttk.Entry(root)
username_entry.pack()

balance_label = ttk.Label(root, text = "Enter your balance (100 to 100000):")
balance_label.pack()
balance_entry = ttk.Entry(root)
balance_entry.pack()

# Create and place input fields and labels
symbol_label = ttk.Label(root, text="Enter the symbol of the cryptocurrency:")
symbol_label.pack()
symbol_entry = ttk.Entry(root)
symbol_entry.pack()

start_date_label = ttk.Label(root, text="Enter the start date (YYYY-MM-DD):")
start_date_label.pack()
start_date_entry = ttk.Entry(root)
start_date_entry.pack()

end_date_label = ttk.Label(root, text="Enter the end date (YYYY-MM-DD):")
end_date_label.pack()
end_date_entry = ttk.Entry(root)
end_date_entry.pack()

submit_button = ttk.Button(root, text="Submit", command=on_submit)
submit_button.pack()

# Create a PanedWindow for displaying plots
paned_window = ttk.PanedWindow(root, orient=tk.VERTICAL)
paned_window.pack(fill=tk.BOTH, expand=True)


returns_frame = ttk.Frame(paned_window, height=100)
paned_window.add(returns_frame)

# Start the Tkinter event loop
root.mainloop()

#Connect to the MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    database="my_db",
    user="root",
    password="Abczxy123(L)"
    )
def retrieve_results_from_json(username):
    try:
        with open("crypto_results.json", "r") as file:
            data = json.load(file)
            print("Retrieved JSON data:", data)
        return data.get(username, [])
    except FileNotFoundError:
        return []


if username := input("Enter the specific name to retrieve the results: "):
    print(f"Retrieving results for '{username}':")
    results = retrieve_results_from_json(username)
    
    for result in results:
        print("--------------------")
        for key, value in result.items():
            print(f"{key}: {value}")
