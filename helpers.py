import os, time
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



def lookup(symbol):
    print(os.environ.get("X-RapidAPI-Key"))

    """Look up quote for symbol."""

    url = "https://yfinance-stock-market-data.p.rapidapi.com/stock-info"

    # Payload for the POST request
    payload = (
        "-----011000010111000001101001\r\n"
        "Content-Disposition: form-data; name=\"symbol\"\r\n\r\n"
        f"{symbol}\r\n"
        "-----011000010111000001101001--\r\n\r\n"
    )

    headers = {
        "X-RapidAPI-Key": os.environ.get("X-RapidAPI-Key"),
        "X-RapidAPI-Host": "yfinance-stock-market-data.p.rapidapi.com",
        "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
    }

    def get_stock_data():
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        stock = response.json()
        stock = stock.get("data",0)
        return stock

    # Contact API
    try:
        stock = get_stock_data()
        # print("STOCK: ", stock)
        # return stock  # Return JSON response if successful
    except requests.RequestException as e:
        print(e)
        # return apology("Issue contacting the API..")
        print("Issue contacting the API..")
        
        time.sleep(1)

        try:
            stock = get_stock_data()
        except:
            return None


    # Parse response
    # try:
        # TODO - Adjust return here to include more stock data.
    return {
        # "name": quote["Global Quote"]["01. symbol"],
        "name": stock["shortName"],
        # "price": float(quote["Global Quote"]["05. price"]),
        "price": float(stock["ask"]),
        # "symbol": quote["Global Quote"]["01. symbol"],
        "symbol": stock["symbol"],
        # "low": float(quote["Global Quote"]["03. high"]),
        "low": float(stock["dayLow"]),
        # "high": float(quote["Global Quote"]["04. low"]),
        "high": float(stock["dayLow"]),
    }
    # except (KeyError, TypeError, ValueError):
        # return apology("Error parsing the API response..")
    

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# TOTO
# Create helper function to reutrn top popular symbols
