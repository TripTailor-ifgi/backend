from app.db import get_db_connection

def fetch_pois_within_buffer(longitude, latitude, buffer_distance):
    """
    Fetch points of interest (amenities) within a buffer around a given coordinate.
    """
    query = """
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
            AND tags->'amenity' = 'cafe'
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query, (longitude, latitude, buffer_distance))
    rows = cursor.fetchall()
    connection.close()

    # Process and return results as a list of dictionaries
    column_names = [desc[0] for desc in cursor.description]
    results = []
    for row in rows:
        row_data = {column_names[i]: row[i] for i in range(len(row))}
        results.append(row_data)
    return results
