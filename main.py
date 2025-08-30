from instaScrapping.api.google_api import GoogleApi
from instaScrapping.api.apify_api import InstaScraper
# find places (bars) near a location using Google Maps API
g = GoogleApi()
bars = g.find_bars(radius=1)
bar = bars[0]
i = InstaScraper()
search_text = f"{bar['name']} {bar['address']}"
i.get_posts(search_text)