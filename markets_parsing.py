from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
from steamcrawl import Request
from pandas import to_datetime

# Reading the 'steam_login_secure' from a file
with open('steam_login_secure.txt', 'r') as file:
    steam_login_secure = file.read()

# Initializing a Request object with the steam login credentials
request = Request(steam_login_secure)


def get_page_html(page: int):
    """Retrieve HTML content of a specific Steam Community Market page."""
    # Setting up Chrome WebDriver with headless option
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    # Accessing the specified page on the Steam Community Market
    driver.get(f"https://steamcommunity.com/market/search?appid=252490#p{page}_price_desc")

    # Waiting for 5 seconds to ensure the page loads completely
    sleep(5)

    # Returning the page source
    return driver.page_source


def get_item_names_from_html(page_html):
    """Extract item names from the given HTML page source."""
    # Parsing the HTML content using BeautifulSoup
    soup = BeautifulSoup(page_html, 'html.parser')

    # Finding all items with a 'data-hash-name' attribute
    items = soup.find_all(attrs={"data-hash-name": True})

    # Extracting the names of items
    return [item['data-hash-name'] for item in items]


def get_item_realistic_steam_price_from_name_try(item_name):
    """Attempt to fetch and calculate a realistic Steam price for a given item."""
    # Fetching price history for the specified item
    data_frame = request.get_price_history(item_name=item_name, appid="252490")

    # Converting the 'date' column to datetime format
    data_frame['date'] = to_datetime(data_frame['date'], format="%b %d %Y")

    # Finding the most recent date in the data
    last_date = data_frame['date'].max()

    # Calculating the first day of the previous month
    first_day_of_last_month = last_date.replace(day=1)

    # Filtering data for the last month
    last_month_data = data_frame[(data_frame['date'] >= first_day_of_last_month) & (data_frame['date'] <= last_date)]

    # Grouping by date and finding the minimum price for each day
    daily_min_prices = last_month_data.groupby('date')['median_price'].min()

    # Calculating the average of these daily minimum prices
    average_of_daily_min = daily_min_prices.mean()

    # Adjusting the price to make it more realistic
    realistic_price = average_of_daily_min * 1.04
    realistic_price_in_usd = round(realistic_price * 1.09, 2)
    return realistic_price_in_usd


def get_item_avg_dmarket_price_from_name_try(item_name):
    """Attempt to fetch and calculate the average DMarket price for a given item."""
    # Setting up parameters for the API request
    params = {
        'title': f'{item_name}',
        'gameId': 'rust',
        'period': '1M',
    }

    # Making a GET request to the DMarket API and parsing the average price
    price_list = get('https://api.dmarket.com/trade-aggregator/v1/avg-sales-graph', params=params).json()['avgPrice']
    price_list_num = [float(price) for price in price_list]

    try:
        # Calculating the average price
        avg_price = round(sum(price_list_num) / len(price_list_num) * 0.95, 2)
    except ZeroDivisionError:
        # Handling the case where price list is empty
        print(price_list_num)
        avg_price = 0
    return avg_price


def get_item_realistic_steam_price_from_name(item_name):
    """Wrapper function to fetch realistic Steam price with error handling."""
    try:
        return get_item_realistic_steam_price_from_name_try(item_name)
    except Exception as e:
        print(f"Error encountered: {e}")
        return get_item_realistic_steam_price_from_name(item_name)


def get_item_avg_dmarket_price_from_name(item_name):
    """Wrapper function to fetch average DMarket price with error handling."""
    try:
        return get_item_avg_dmarket_price_from_name_try(item_name)
    except Exception as e:
        print(f"Error encountered: {e}")
        return get_item_avg_dmarket_price_from_name(item_name)
