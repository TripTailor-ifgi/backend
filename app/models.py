from app.db import get_db_connection
from app.utils.csv_loader import load_csv

def get_option_mapping():
    """
    Build a mapping of options to database columns from the CSV file.
    """
    try:
        file_path = "app/data/categories_options_point.csv"  # Update this path as needed
        data = load_csv(file_path)  # Assuming this loads the CSV into a list of dictionaries

        # Create a dictionary mapping each option to its respective column
        mapping = {}
        for row in data:
            for column, value in row.items():
                if value:  # Skip empty cells
                    mapping[value] = column

        return mapping
    except Exception as e:
        print("Error in get_option_mapping:", str(e))  # Log the specific error
        raise


def fetch_pois_flexible(longitude, latitude, buffer_distance, filters):
    """
    Fetch points of interest dynamically based on filters.
    """
    try:
        # Base SQL query
        base_query = """
            SELECT 
                *, 
                ST_AsGeoJSON(way) AS geometry, 
                CONCAT(tags->'addr:street', ' ', tags->'addr:housenumber') AS address
            FROM 
                public.planet_osm_point p
            WHERE
                ST_Contains(
                    ST_Transform(
                        ST_Buffer(
                            ST_Transform(
                                ST_SetSRID(ST_MakePoint(%s, %s), 4326), 
                                25832
                            ), 
                            %s
                        ),
                        4326
                    ), 
                    p.way
                )
                AND tags ? 'addr:street'
        """

        filter_conditions = []
        filter_values = [longitude, latitude, buffer_distance]

        # Process each filter
        for filter_entry in filters:
            option = filter_entry.get('option')
            vegan = filter_entry.get('vegan', False)

            if option == "cafe" or option == "restaurant" or option == "fast_food":
                if vegan:
                    # Add vegan-specific filtering
                    filter_conditions.append("""
                        (amenity = %s AND 
                         (tags->'diet:vegan' = 'yes' OR tags->'diet:vegan' = 'only'))
                    """)
                else:
                    # Add non-vegan general filter
                    filter_conditions.append("amenity = %s")
            else:
                # General filtering for other options
                filter_conditions.append("amenity = %s")

            filter_values.append(option)

        # Combine all conditions
        if filter_conditions:
            base_query += " AND (" + " OR ".join(filter_conditions) + ")"

        # Debugging: Log the query and values
        print("Generated SQL Query:", base_query)
        print("With values:", filter_values)

        # Execute query
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(base_query, tuple(filter_values))
        rows = cursor.fetchall()
        connection.close()

        # Process results
        column_names = [desc[0] for desc in cursor.description]
        results = [{column_names[i]: row[i] for i in range(len(row))} for row in rows]

        return results
    except Exception as e:
        print("Error in fetch_pois_flexible:", str(e))
        raise