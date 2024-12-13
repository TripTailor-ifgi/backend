import csv


def load_csv(file_path):
    """
    Load a CSV file and return its content as a list of dictionaries.
    """
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        return [row for row in reader]


def get_categories_and_options():
    """
    Process the CSV data to extract categories and their options.
    :return: Dictionary with categories as keys and their options as lists.
    """
    file_path = "app/data/categories_options_point.csv"
    data = load_csv(file_path)

    categories = {}
    for column in data[0].keys():  # Assumes the first row is headers
        categories[column] = [row[column] for row in data if row[column]]

    return categories
