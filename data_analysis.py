from pandas import DataFrame
from time import sleep
from markets_parsing import (
    get_item_realistic_steam_price_from_name,
    get_item_avg_dmarket_price_from_name,
    get_page_html,
    get_item_names_from_html
)


def get_all_item_value_ratios_df(item_names: list):
    """Creates a DataFrame containing value ratios of items between Steam and DMarket."""

    # Initializing a DataFrame with specified columns
    df = DataFrame(columns=['item_name', 'realistic_steam_price', 'dmarket_avg_price', 'value_ratio', 'link'])

    for item_name in item_names:
        # Fetching realistic Steam price for the item
        realistic_steam_price = get_item_realistic_steam_price_from_name(item_name)

        # Fetching average DMarket price for the item
        avg_dmarket_price = get_item_avg_dmarket_price_from_name(item_name)

        # Calculating the value ratio between DMarket and Steam prices
        value_ratio = round(avg_dmarket_price / realistic_steam_price, 3)

        # Appending the collected data to the DataFrame
        df.loc[len(df.index)] = [
            item_name,
            realistic_steam_price,
            avg_dmarket_price,
            value_ratio,
            f'https://steamcommunity.com/market/listings/252490/{item_name}'
        ]

        # Introducing a delay to prevent rapid requests
        sleep(2)

    # Sorting the DataFrame based on the value ratio in descending order and resetting index
    return df.sort_values(by='value_ratio', ascending=False, ignore_index=True)


def generate_items_df_from_page(page):
    """Generates a DataFrame of item values from a specified Steam Community Market page."""

    # Retrieving HTML content of the specified page
    html = get_page_html(page)

    # Extracting item names from the HTML content
    names = get_item_names_from_html(html)

    # Generating and returning a DataFrame with item value ratios
    return get_all_item_value_ratios_df(names)
