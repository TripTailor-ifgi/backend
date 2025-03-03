import json
from app.db import get_db_connection
import logging

def check_possible_options(start_longitude, start_latitude, buffer_distance, filters):
    try:
        possible_options = []
        options_amenities = ['bar', 'pub', 'cafe', 'fast_food', 'ice_cream', 'restaurant']
        options_tourism = ['attraction', 'gallery', 'museum', 'zoo', 'park']

        connection = get_db_connection()
        cursor = connection.cursor()

        # Helper function to build filter conditions
        def build_filter_query(location_type, location_subtype):
            filter_conditions = []
            filter_values = []

            if location_type == "amenity":
                if location_subtype == "bar":
                    filter_conditions.append("amenity IN (%s, 'pub') AND tags ? 'addr:street'")
                    filter_values.append(location_subtype)
                else:
                    filter_conditions.append("amenity = %s AND tags ? 'addr:street'")
                    filter_values.append(location_subtype)

                if filters.get('BarrierFree'):
                    filter_conditions.append("tags->'wheelchair' = 'yes'")

                if filters.get('Vegan') and location_subtype not in ['bar', 'pub']:
                    filter_conditions.append("(tags->'diet:vegan' = 'yes' OR tags->'diet:vegan' = 'only')")

            elif location_subtype == "park":
                filter_conditions.append("leisure = %s AND name IS NOT NULL")
                filter_values.append(location_subtype)

            elif location_type == "tourism":
                filter_conditions.append("tourism = %s")
                filter_values.append(location_subtype)

                if filters.get('BarrierFree'):
                    filter_conditions.append("tags->'wheelchair' = 'yes'")

            filter_query = " AND ".join(filter_conditions)
            return f" AND ({filter_query})", filter_values

        # Helper function to build query for each option
        def build_query(option, location_type):
            if option in ['park', 'museum']:
                table = "planet_osm_polygon"
                geometry_field = "ST_Centroid(way)"
            else:
                table = "planet_osm_point"
                geometry_field = "way"

            filter_condition, filter_values = build_filter_query(location_type, option)

            query = f"""
                SELECT name
                FROM {table} p
                WHERE ST_DWithin(
                        ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 25832),
                        ST_Transform({geometry_field}, 25832),
                        %s
                    )
                    {filter_condition}
                LIMIT 1
            """
            return query, [start_longitude, start_latitude, buffer_distance] + filter_values

        # Check amenities
        bar_found = False
        for amenity in options_amenities:
            if amenity == 'pub' and bar_found:
                continue  # Skip checking for pub if bar is found

            query, query_values = build_query(amenity, 'amenity')
            cursor.execute(query, query_values)
            result = cursor.fetchone()
            if result:
                if amenity == 'bar':
                    bar_found = True
                possible_options.append({"amenity": amenity})

        # Check tourism spots
        for tourism in options_tourism:
            query, query_values = build_query(tourism, 'tourism')
            cursor.execute(query, query_values)
            result = cursor.fetchone()
            if result:
                possible_options.append({"tourism": tourism})

        connection.close()
        return possible_options

    except Exception as e:
        logging.error(f"Error in check_possible_options: {e}")
        return []


def fetch_pois_flexible(start_longitude, start_latitude, buffer_distance, locations, filters, date):
    try:
        all_results = []
        closest_results = []
        visited_locations = set()  # Track visited locations by name

        current_longitude = start_longitude
        current_latitude = start_latitude

        connection = get_db_connection()
        cursor = connection.cursor()

        for location in locations:
            location_type = location.get('top', '').lower()
            location_subtype = location.get('sub', '').lower()

            if location_type == "start":
                continue

            if location_subtype in {"museum", "park"}:
                table = "public.planet_osm_polygon"
                geometry_field = "ST_AsGeoJSON(ST_Centroid(way)) AS geometry"
            else:
                table = "public.planet_osm_point"
                geometry_field = "ST_AsGeoJSON(way) AS geometry"

            filter_condition, filter_values, detailed_type = build_filter_query(location_type, location_subtype, filters)

            # Exclude previously visited locations
            exclusion_clause = ""
            if visited_locations:
                exclusion_clause = "AND name NOT IN (%s)" % ', '.join(['%s'] * len(visited_locations))
                filter_values.extend(visited_locations)

            query_all = f"""
                SELECT DISTINCT
                    name,
                    {geometry_field},
                    CONCAT(tags->'addr:street', ' ', tags->'addr:housenumber') AS address,
                    ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326),25832) <-> ST_Transform(p.way,25832) AS distance,
                    tags->'opening_hours' AS opening_hours,
                    tags->'wheelchair' AS wheelchair,
                    tags->'diet:vegan' AS vegan
                FROM 
                    {table} p
                WHERE
                    ST_DWithin(
                        ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 25832), 
                        ST_Transform(p.way, 25832), 
                        %s
                    )
                    {filter_condition}
                    {exclusion_clause}
                ORDER BY distance ASC
            """

            query_values = [current_longitude, current_latitude, current_longitude, current_latitude, buffer_distance] + filter_values

            cursor.execute(query_all, tuple(query_values))
            rows = cursor.fetchall()

            column_names = [desc[0] for desc in cursor.description]
            location_results = [{column_names[i]: row[i] for i in range(len(row))} for row in rows]

            if location_results:
                # Add to results list
                all_results.append({
                    "location_type": detailed_type,
                    "results": location_results
                })

                closest_results.append({
                    "location_type": detailed_type,
                    "results": [location_results[0]]
                })

                # Store visited location name to avoid selecting it again
                visited_locations.add(location_results[0]['name'])

                # Update current location for the next search
                first_result = location_results[0]['geometry']
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

    if location_type == "amenity":
        if location_subtype.lower() == "bar":
            filter_conditions.append("amenity in (%s, 'pub') AND tags ? 'addr:street'")
            filter_values.append(location_subtype.lower())
        else:
            filter_conditions.append("amenity = %s AND tags ? 'addr:street'")
            filter_values.append(location_subtype.lower())

        if filters.get('BarrierFree'):
            filter_conditions.append("tags->'wheelchair' = 'yes'")

        if filters.get('Vegan') and location_subtype.lower() not in ['bar', 'pub']:
            filter_conditions.append("(tags->'diet:vegan' = 'yes' OR tags->'diet:vegan' = 'only')")

    elif location_subtype.lower() == "park":
        filter_conditions.append("leisure = %s AND name IS NOT NULL")
        filter_values.append(location_subtype.lower())

    elif location_type == "tourism":
        filter_conditions.append("tourism = %s")
        filter_values.append(location_subtype.lower())

        if filters.get('BarrierFree'):
            filter_conditions.append("tags->'wheelchair' = 'yes'")

    filter_query = " AND ".join(filter_conditions)
    return f" AND ({filter_query})", filter_values, detailed_type

def parse_geojson_coords(geojson):
    geo_data = json.loads(geojson)
    lon, lat = geo_data['coordinates']
    return {"lat": lat, "lon": lon}