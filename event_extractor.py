import re
from typing import Optional

import dateparser

from instaScrapping.db.models import Event


def extract_event_info(text: str) -> Optional[Event]:
    """
    Analyzes a string of text to extract event information.

    Args:
        text: The string containing the event description.

    Returns:
        An Event object populated with the extracted information.
    """

    # Instantiate the Event object to store results
    event_info = Event()

    lines = text.strip().split('\n')
    remaining_text = text

    # --- 1. Extract Event Name ---
    # Look for a line that is mostly uppercase, which is often the title.
    for i, line in enumerate(lines):
        # Remove anything that isn't an uppercase letter or whitespace to check its ratio
        clean_line = re.sub(r'[^A-ZÀ-Ú\s]', '', line.upper())
        if len(clean_line.strip()) > 5 and (len(clean_line) / len(line) > 0.7 if len(line) > 0 else 0):
            event_info.name = line.strip()
            # Remove the title line from the text so it's not in the description
            remaining_text = remaining_text.replace(line, "", 1)
            break

    # --- 2. Extract Date ---
    # Use dateparser.search.search_dates for flexible date parsing.
    # Set PREFER_DATES_FROM to 'future' to correctly interpret dates without a year.
    settings = {'PREFER_DATES_FROM': 'future', 'DATE_ORDER': 'DMY'}
    # Correctly call the function from the 'search' module
    found_dates = dateparser.parse(text, languages=['it'], date_formats=['%d %B'])
    if not found_dates:
        return None
    # Take the first valid date found
    event_info.date = found_dates[0][1].strftime('%Y-%m-%d')
    # Remove the date string from the remaining text
    remaining_text = remaining_text.replace(found_dates[0][0], "", 1)

    # --- 3. Extract Time (Start and End) ---
    # Regex to find times like "22.00", "22:00", "dalle 22", or ranges like "21:00 - 23:30"
    time_pattern = re.compile(
        r'(?:dalle\sore|dalle|alle|ore)?\s*(\d{1,2}[:.]\d{2}|\d{1,2})\s*(?:-\s*(\d{1,2}[:.]\d{2}|\d{1,2}))?',
        re.IGNORECASE)
    found_times = time_pattern.findall(remaining_text)

    if found_times:
        # Take the first start time found and normalize it
        event_info.start_time = found_times[0][0].replace('.', ':')
        # If an end time is found in the "start - end" format
        if found_times[0][1]:
            event_info.end_time = found_times[0][1].replace('.', ':')

        # Remove the found time strings from the remaining text
        for match in time_pattern.finditer(remaining_text):
            remaining_text = remaining_text.replace(match.group(0), "", 1)

    # --- 4. Extract Price ---
    # Regex for prices like "€10", "10€", "10 euro", or "ingresso libero"
    price_pattern = re.compile(r'(\d+[\.,]?\d*\s*€|€\s*\d+[\.,]?\d*|\d+\s*euro|ingresso\s*libero|gratuito)',
                               re.IGNORECASE)
    found_price = price_pattern.search(text)
    if found_price:
        event_info.price = found_price.group(1).strip()
        remaining_text = remaining_text.replace(found_price.group(1), "", 1)

    # --- 5. Consolidate Description ---
    # Clean up the remaining text to create the description.
    description_lines = [line.strip() for line in remaining_text.strip().split('\n') if line.strip()]
    event_info.description = " ".join(description_lines)

    return event_info


# --- Example Usage ---
sample_text_1 = """
🗓Venerdì 6 Giugno PRO LOCO MONTECCHIA presenta: 🌟ＡＦＲＯ ＶＩＢＥＳ ＳＵＭＭＥＲ ＴＯＵＲ ２０２５🌟 Unisciti a noi per una serata magica,dove il ritmo incontrerà la bellezza del cielo stellato! 📍Luogo: Piazza Umberto I,37030 Montecchia di Crosara (Vr) 🍝🍔 Ricco stand gastronomico DALLE 22.00 🎧DJ Morgan 🎙Andrea Meggio Preparatevi a ballare, a divertirvi e vivere una notte indimenticabile sotto le stelle. Non mancate!🌟❤️
"""

# Another example with a price and end time
sample_text_2 = """
Charity Concert
Saturday 13 September, don't miss the chance to help!
From 21:00 - 23:30 at the Municipal Theater.
Admission: 15€, proceeds will go to charity.
"""

# Extract information
event_data_1 = Event.Schema().dump(extract_event_info(sample_text_1))
event_data_2 = Event.Schema().dump(extract_event_info(sample_text_2))

# Print results in a readable JSON format
import json

print("--- Results for Sample Text 1 ---")
print(json.dumps(event_data_1, indent=4, ensure_ascii=False))

print("\n--- Results for Sample Text 2 ---")
print(json.dumps(event_data_2, indent=4, ensure_ascii=False))