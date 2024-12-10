from app.db import get_db_connection


def fetch_museums_by_city(city):
    query = """
        SELECT 
            *, 
            ST_AsGeoJSON(way) AS geometry, 
            CONCAT(tags->'addr:street', ' ', tags->'addr:housenumber') AS address
        FROM 
            planet_osm_polygon
        WHERE 
            tags->'addr:city' = 'Münster'
            AND tourism = 'museum';
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query, (city,))
    rows = cursor.fetchall()
    connection.close()

    # Assuming the columns you want are known, define column names here:
    column_names = [desc[0] for desc in cursor.description]

    results = []
    for row in rows:
        row_data = {column_names[i]: row[i] for i in range(len(row))}
        results.append(row_data)
    return results