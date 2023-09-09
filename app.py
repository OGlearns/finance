import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["ENV"] = "development"

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use Postgres database

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)





# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

    # pk_2a9957ac066c48ba8fb1dadb24530f09 API KEY for reference

#Make necessary tables for data records
db.execute("CREATE TABLE IF NOT EXISTS history (transaction_id SERIAL PRIMARY KEY NOT NULL, shares NUMERIC NOT NULL, symbol TEXT NOT NULL, price NUMERIC NOT NULL, timestamp TIMESTAMP DEFAULT NOW() NOT NULL, id INTEGER, FOREIGN KEY (id) REFERENCES users (id))")
db.execute("CREATE INDEX IF NOT EXISTS history_symbol_shares_id_price_time_index ON history (id, symbol, shares, price, timestamp)")
db.execute("CREATE INDEX IF NOT EXISTS users_id_username_hash_cash_index ON users (id, username, hash, cash)")


#db.execute("CREATE INDEX IF NOT EXISTS )

def user_balance ():
    user_shares = db.execute("SELECT symbol, SUM(shares) AS shares_sum FROM history WHERE id = ? GROUP BY symbol", session["user_id"])

    if not user_shares:
        return render_template ("index.html", money = 10000, total = 10000)

    else:
        money = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        total = money

        for row in user_shares:
            print('row in user_shares: ', row)
            print('user_shares: ', user_shares)
            row["symbol"] = lookup(row["symbol"])["symbol"]
            print('lookup(row["symbol"])["price"]: ', lookup(row["symbol"])["price"])
            row["price"] = lookup(row["symbol"])["price"]
            print('row["price"]: ', row["price"])
            total += row["price"] * row["shares_sum"]
            shares = row["shares_sum"]
        return render_template ("index.html", user_shares=user_shares, money=money, total=total, shares=shares)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    if request.method == "POST" or "GET":
        return user_balance()


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        symbol = request.form.get("symbol")

        if not symbol:
            return apology("Must enter a valid symbol")

        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("Must enter valid number of shares", 400)


        if not int(shares) or int(shares) < 1:
            return apology("Must enter positive value for shares", 400)

        stock = lookup(symbol)

        if not stock:
            return apology("Must enter a valid ticker")

        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        buying_price = stock["price"] * shares
        if buying_price > user_cash:
            return apology("Not enough cash to purchase shares")
        else:
            db.execute("INSERT INTO history (id, symbol, shares, price) VALUES(?,?,?,?)", session["user_id"], symbol, shares, buying_price)

            #update the users cash amount
            user_cash = user_cash - buying_price
            db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash, session["user_id"])
            flash("Shares successfully purchased!")
        return user_balance()
    else:

        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    if request.method == "POST" or "GET":

        user_transactions = db.execute("SELECT symbol, shares, price, timestamp FROM history WHERE id = ?", session["user_id"])

        if not user_transactions:
            return render_template("/history.html")

        else:
            return render_template("/history.html", user_transactions=user_transactions)

    return render_template("/history.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Successfully logged in")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    flash("Logged out!")
    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide stock symbol for lookup")

        quote = lookup(symbol)
        if not quote:
            return apology("must provide a valid stock symbol")
        else:
            return render_template("/quoted.html", quote=quote, symbol=symbol)


    else:
        return render_template("/quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords much match", 400)

        hash_value = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=16)
        username = request.form.get("username")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 0:
            return apology("Username is taken, please enter a different username", 400)

        else:
            db.execute("INSERT INTO users(username, hash) VALUES(?,?)", username, hash_value)

        users = db.execute("SELECT * FROM users WHERE username = ?", username)

        session["user_id"] = users[0]["id"]
        flash("Successfully registered!")
        return redirect("/login")

    else:
        return render_template("/register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    #all_users_stocks = db.execute("SELECT symbol, SUM(shares) FROM history WHERE id = ? GROUP BY symbol", session["user_id"])[0]["symbol"]

    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if not symbol:
            return apology("Valid stock symbol must be selected to sell")
        if not shares or shares < 1:
            return apology("Must enter positive number of shares")

        stock = lookup(symbol)
        stock_price = stock["price"]

        # check to see if they own enough of the stock to sell

        owned_shares = db.execute("SELECT symbol, sum(shares) as shares_sum FROM history WHERE id = ? AND symbol = ? GROUP BY symbol", session["user_id"], symbol)[0]["shares_sum"]

#         owned_shares = db.execute("SELECT symbol, sum(shares) FROM history WHERE id, symbol = %s GROUP BY symbol", (session["user_id"], symbol))[0]["sum(shares)"]


        if not owned_shares:
            return apology("Must enter valid number of shares")

        elif owned_shares < shares:
            return apology("Not enough shares to sell")
        else:
            #calculate sale money
            sale_money = stock_price * shares

            #insert selling transaction into history table
            db.execute("INSERT INTO history (id, symbol, shares, price) VALUES(?,?,?,?)", session["user_id"], symbol, -abs(shares), stock_price)

            #add sale money to user cash
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", sale_money, session["user_id"])
            flash("Shares successfully sold!")
        # return render_template("/index.html", user_shares=user_shares, money=money, total=total, shares=shares)
        return user_balance()

    elif request.method == "GET":
        all_users_stocks = db.execute("SELECT symbol FROM history WHERE id = %s GROUP BY symbol", session["user_id"])
        return render_template("/sell.html", all_users_stocks=all_users_stocks)
