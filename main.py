from data_analysis import generate_items_df_from_page
from pandas import concat


def generate_csv_for_pages_range(pages_range: range):
    """Generates a CSV file containing item value ratios from a range of pages."""

    # List to store DataFrames from each page
    dataframes = []

    # Looping through each page in the specified range
    for page in pages_range:
        # Generating a DataFrame for each page and adding it to the list
        dataframes.append(generate_items_df_from_page(page))

    # Concatenating all the DataFrames into one
    combined_df = concat(dataframes, ignore_index=True)

    # Sorting the combined DataFrame by 'value_ratio' in descending order
    # and exporting it to a CSV file without the index column
    combined_df \
        .sort_values(by='value_ratio', ascending=False, ignore_index=True) \
        .to_csv("table_of_items_with_value_ratios.csv", index=False)


# Calling the function to generate the CSV for the specified page range
generate_csv_for_pages_range(range(3, 15))
