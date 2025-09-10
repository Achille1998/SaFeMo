# -*- coding: utf-8 -*-
"""
Questo script si connette alle API di Apify per eseguire un Actor
e recuperare i dati estratti.
"""

from apify_client import ApifyClient
import os
from dotenv import load_dotenv

from db.models import Place

load_dotenv()

APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN')
TASK_IDs = {"FindProfile": "eLhqgdpeZhnhVArft",
            "FindPostsFromURLS": "ZDiUAjexvWt4t2NSh"}


class ApifyApiInterface:
    def __init__(self):
        try:
            self.apify_client = ApifyClient(APIFY_API_TOKEN)
            print("✅ Client di Apify inizializzato correttamente.")
        except Exception as e:
            print(f"❌ Errore durante l'inizializzazione del client: {e}")
            exit()

    def get_posts(self, urls: list):
        task_input = {
            "resultsLimit": 10,
            "resultsType": "posts",
            "searchType": "url",
            "urls": urls
        }
        TASK_ID = TASK_IDs["FindPostsFromURLS"]

        print(f"\n🚀 Esecuzione del task...")

        try:
            # Esegue l'Actor e attende il suo completamento
            run_actor = self.apify_client.task(TASK_ID).call(task_input=task_input)
            print(f"✅ Actor eseguito con successo. ID dell'esecuzione (Run ID): {run_actor['id']}")
        except Exception as e:
            print(f"❌ Errore durante l'esecuzione dell'Actor: {e}")
            exit()

        try:
            # Itera sugli elementi presenti nel dataset dell'esecuzione appena conclusa
            dataset_items = self.apify_client.dataset(run_actor["defaultDatasetId"]).list_items().items

            print(f"✅ Risultati ottenuti! Trovati {len(dataset_items)} elementi.")

            # Stampa i risultati ottenuti
            for item in dataset_items:
                # Questo esempio stampa l'URL e il titolo della pagina estratta
                print(f"  - URL: {item.get('url')}, Titolo: {item.get('title')}")

        except Exception as e:
            print(f"❌ Errore durante il recupero dei risultati: {e}")

        print("\n🎉 Script terminato.")

    def get_profile(self, research_text: str):
        task_input = {
            "addParentData": False,
            "enhanceUserSearchWithFacebookPage": False,
            "isUserReelFeedURL": False,
            "isUserTaggedFeedURL": False,
            "search": research_text,
            "searchLimit": 1,
            "searchType": "user"
        }
        TASK_ID = TASK_IDs["FindProfile"]

        print(f"\n🚀 Esecuzione del task...")

        try:
            # Esegue l'Actor e attende il suo completamento
            run_actor = self.apify_client.task(TASK_ID).call(task_input=task_input)
            print(f"✅ Actor eseguito con successo. ID dell'esecuzione (Run ID): {run_actor['id']}")
        except Exception as e:
            print(f"❌ Errore durante l'esecuzione dell'Actor: {e}")
            exit()

        try:
            # Itera sugli elementi presenti nel dataset dell'esecuzione appena conclusa
            dataset_items = self.apify_client.dataset(run_actor["defaultDatasetId"]).list_items().items
            return dataset_items[0] if len(dataset_items) > 0 else None

        except Exception as e:
            print(f"❌ Errore durante il recupero dei risultati: {e}")

    def get_profile_from_place(self, place: Place):
        return self.get_profile(place.name + " " + place.address)

    def get_posts_from_places(self, places: list[Place]):
        self.get_posts([place.instagram_URL for place in places])
