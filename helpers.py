import os
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
    """Look up quote for symbol."""

    # Contact API
    try:
        url = "https://alpha-vantage.p.rapidapi.com/query"
        querystring = {"function":"GLOBAL_QUOTE","symbol":symbol,"datatype":"json"}
        headers = {
        	"X-RapidAPI-Key": os.environ.get("X-RapidAPI-Key"),
        	"X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        print(quote)
        print(float(quote["Global Quote"]["05. price"]))
        return {
            "name": quote["Global Quote"]["01. symbol"],
            "price": float(quote["Global Quote"]["05. price"]),
            "symbol": quote["Global Quote"]["01. symbol"],
            "low": float(quote["Global Quote"]["03. high"]),
            "high": float(quote["Global Quote"]["04. low"]),
        }
    except (KeyError, TypeError, ValueError):
        
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# TOTO
# Create helper function to reutrn top popular symbols
