import json
import datetime
from app.db import get_db_connection

def fetch_pois_flexible(start_longitude, start_latitude, buffer_distance, locations, filters, date):
    try:
        all_results = []
        closest_results = []

        current_longitude = start_longitude
        current_latitude = start_latitude

        connection = get_db_connection()
        cursor = connection.cursor()

        for index, location in enumerate(locations):
            location_type = location.get('top').lower()
            location_subtype = location.get('sub').lower()

            if location_type == "start":
                continue

            if location_subtype.lower() in {"museum", "park"}:
                table = "public.planet_osm_polygon"
                geometry_field = "ST_AsGeoJSON(ST_Centroid(way)) AS geometry"
            else:
                table = "public.planet_osm_point"
                geometry_field = "ST_AsGeoJSON(way) AS geometry"

            filter_condition, filter_values, detailed_type = build_filter_query(location_type, location_subtype, filters)

            query_all = f"""
                SELECT DISTINCT
                    name,
                    {geometry_field},
                    CONCAT(tags->'addr:street', ' ', tags->'addr:housenumber') AS address,
                    ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 25832) <-> ST_Transform(p.way, 25832) AS distance,
                    tags->'opening_hours' AS opening_hours,
                    tags->'wheelchair' AS wheelchair
                FROM 
                    {table} p
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
                    {filter_condition}
                ORDER BY distance ASC
            """

            query_values = [current_longitude, current_latitude, current_longitude, current_latitude, buffer_distance] + filter_values

            cursor.execute(query_all, tuple(query_values))
            rows = cursor.fetchall()

            column_names = [desc[0] for desc in cursor.description]
            location_results = []
            for row in rows:
                row_dict = {column_names[i]: row[i] for i in range(len(row))}
                location_results.append(row_dict)

            if location_results:
                all_results.append({
                    "location_type": detailed_type,
                    "results": location_results
                })

                closest_result = location_results[0]
                closest_results.append({
                    "location_type": detailed_type,
                    "results": [closest_result]
                })

                first_result = closest_result['geometry']
                coords = parse_geojson_coords(first_result)
                current_longitude, current_latitude = coords['lon'], coords['lat']

        connection.close()
        return all_results, closest_results

    except Exception as e:
        print("Error fetching POIs:", str(e))
        return [], []

def build_filter_query(location_type, location_subtype, filters):
    filter_conditions = []
    filter_values = []
    detailed_type = f"{location_type}_{location_subtype.lower()}"

    if location_type == "amenities":
        filter_conditions.append("amenity = %s AND tags ? 'addr:street'")
        filter_values.append(location_subtype.lower())

        if filters.get('barrierFree'):
            filter_conditions.append("tags->'wheelchair' = 'yes'")

        if filters.get('vegan') and location_subtype.lower() not in ['bar', 'pub']:
            filter_conditions.append("(tags->'diet:vegan' = 'yes' OR tags->'diet:vegan' = 'only')")

    elif location_subtype.lower() == "park":
        filter_conditions.append("leisure = %s AND name IS NOT NULL")
        filter_values.append(location_subtype.lower())

    elif location_type == "tourism":
        filter_conditions.append("tourism = %s")
        filter_values.append(location_subtype.lower())

        if filters.get('barrierFree'):
            filter_conditions.append("tags->'wheelchair' = 'yes'")

    filter_query = " AND ".join(filter_conditions)
    return f" AND ({filter_query})", filter_values, detailed_type

def parse_geojson_coords(geojson):
    geo_data = json.loads(geojson)
    lon, lat = geo_data['coordinates']
    return {"lat": lat, "lon": lon}