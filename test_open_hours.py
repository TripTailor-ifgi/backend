import datetime
import re

def parse_opening_hours(opening_hours, trip_date):
    """
    Parses and checks if the place is open on the given trip date.

    Args:
        opening_hours (str): The opening hours string from OSM tags.
        trip_date (str): The trip date in "YYYY-MM-DD" format.

    Returns:
        bool: True if open, False otherwise.
    """

    # Handle cases where hours are appointment-based
    if "Nach Absprache" in opening_hours or "Nach Vereinbarung" in opening_hours:
        return True  # Consider always open

    # Convert trip date to weekday abbreviation and month
    trip_datetime = datetime.datetime.strptime(trip_date, "%Y-%m-%d")
    weekday_abbr = trip_datetime.strftime("%a")[:2]  # 'Mo', 'Tu', etc.
    trip_month = trip_datetime.strftime("%b")  # 'Jan', 'Feb', etc.

    # Normalize string for easier parsing
    opening_hours = opening_hours.replace(" ", "")

    # Check if explicitly closed
    if f"{weekday_abbr}off" in opening_hours:
        return False  # Closed on this day

    # Handle standard weekly hours (e.g., "Mo-Fr 10:00-18:00; Sa-Su 11:00-17:30")
    weekly_pattern = re.compile(r"((?:Mo|Tu|We|Th|Fr|Sa|Su)(?:-(?:Mo|Tu|We|Th|Fr|Sa|Su))?|(?:Mo|Tu|We|Th|Fr|Sa|Su)(?:,(?:Mo|Tu|We|Th|Fr|Sa|Su))*)\s*(\d{2}:\d{2}-\d{2}:\d{2})")
    matches = weekly_pattern.findall(opening_hours)

    for match in matches:
        day_part, _ = match

        # Handle ranges like "Tu-Su"
        if "-" in day_part:
            start_day, end_day = day_part.split("-")
            day_order = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
            start_index = day_order.index(start_day)
            end_index = day_order.index(end_day)

            # Handle week wrap-around case (e.g., "Su-Mo")
            if start_index <= end_index:
                if weekday_abbr in day_order[start_index:end_index + 1]:
                    return True
            else:
                if weekday_abbr in day_order[start_index:] or weekday_abbr in day_order[:end_index + 1]:
                    return True

        # Handle comma-separated days like "Mo,We,Th"
        elif "," in day_part:
            valid_days = day_part.split(",")
            if weekday_abbr in valid_days:
                return True

        else:
            if weekday_abbr == day_part:
                return True

    # Handle seasonal hours (e.g., "Mar-Oct: Tu-Su 10:00-18:00")
    season_pattern = re.compile(r"([A-Za-z]{3})-([A-Za-z]{3}):([A-Za-z,]+)\s*(\d{2}:\d{2}-\d{2}:\d{2})")
    seasonal_matches = season_pattern.findall(opening_hours)

    if seasonal_matches:
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                     "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

        current_month_num = month_map[trip_month]

        for start_month, end_month, days_part, _ in seasonal_matches:
            start_index = month_map[start_month]
            end_index = month_map[end_month]

            if start_index <= current_month_num <= end_index:
                if weekday_abbr in days_part.split(","):
                    return True

    # If no match was found, assume closed
    return False

def run_tests():
    test_cases = [
        ("Tu-Su 10:00-18:00; PH off", "2025-01-18", True),  # Saturday, should be open
        ("Mo off; Tu-Fr 10:00-18:00; Sa-Su 11:00-17:30", "2025-01-13", False),  # Monday, should be closed
        ("Mar-Oct: Tu-Su 10:00-18:00; Nov-Feb: Sa-Su 11:00-17:30", "2025-03-15", True),  # March, should be open
        ("PH,Mo-Su 00:00-24:00", "2025-12-25", True),  # Public holiday, should be open
        ("Nach Absprache", "2025-06-10", True),  # Always open by appointment
        ("We-Fr 12:00-17:00; Sa 12:00-16:00; Su-Tu,PH off", "2025-01-14", False),  # Tuesday, should be closed
        ("Mo-Fr 10:00-18:00; Sa 10:00-14:00; Su,PH off", "2025-01-12", False),  # Sunday, should be closed
        ("Mo-Fr 10:00-18:00; Sa 10:00-14:00; Su,PH off", "2025-01-10", True),  # Friday, should be open
        ("Mo,We,Th 18:00-21:00; Sa,Su 14:00-17:00", "2025-01-11", True),  # Saturday, should be open (previous fail)
        ("Mo,We,Th 18:00-21:00; Sa,Su 14:00-17:00", "2025-01-12", True),  # Sunday, should be open
        ("Mo,We,Th 18:00-21:00; Sa,Su 14:00-17:00", "2025-01-14", False),  # Tuesday, should be closed
    ]

    for opening_hours, test_date, expected in test_cases:
        result = parse_opening_hours(opening_hours, test_date)
        status = "PASS" if result == expected else "FAIL"
        print(f"[{status}] {opening_hours} on {test_date} → Expected: {expected}, Got: {result}")

if __name__ == "__main__":
    run_tests()