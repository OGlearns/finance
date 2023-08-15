## Stock Trading Flask Application README

## Introduction
This is a stock trading Flask application that allows a user to buy and sell stocks. 

## Required Libraries and Technologies
-cs50
-Flask
-Flask-Session
-requests
-gunicorn
-psycopg2-binary
-urllib3==1.26.5

## Key Features
- Buy stocks with fake available cash balance, starting out with $10,000.00
- View portfolio of stocks
- Real-time stock data via a financial API

## Deployment
The application uses the following environment variables to run:
- `API_KEY`: This is the API key required to retrieve real-time stock data. 
- `DATABASE_URL`: This is the URL to the SQL database used to store user data.

## Code Structure
The code is structured as follows:
- The `import` section imports the required libraries and modules
- The `app` object is created and configured to use the filesystem for storing session data and to auto-reload templates. 
- The `db` object is created and configured to use the SQL database defined by the `DATABASE_URL` environment variable. 
- The code creates necessary tables for data records
- The `user_balance` function retrieves the user's cash balance and calculates the total value of their portfolio. 
- The `index` route displays the portfolio page and calls the `user_balance` function to retrieve data.
- The `buy` route handles the buying of stocks by the user. It checks for the availability of funds and updates the user's data in the database.
- The `after_request` function sets response headers to prevent caching.

## Running the Application
To run the application, set the required environment variables and run `flask run` in the terminal.
