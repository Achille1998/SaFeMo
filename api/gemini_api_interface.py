import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

from db.models import Event

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


class GeminiApiInterface:
    def __init__(self):
        generation_config = {
            "temperature": 0.0,
            "response_mime_type": "application/json",
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest', generation_config=generation_config)
        try:
            genai.configure(api_key=API_KEY)
        except Exception as e:
            print(f"Errore nella configurazione dell'API: {e}")
            exit()

    def extrac_event_info(self, testo_input):
        """
        Analizza un testo per estrarre informazioni su un evento utilizzando l'API Gemini.

        Args:
            testo_input (str): Il testo da analizzare.

        Returns:
            dict: Un dizionario contenente le informazioni sull'evento estratte,
                  o un messaggio di errore.
        """
        prompt = """
        Analizza il testo fornito e determina se descrive un evento.
        Se il testo descrive un evento, estrai le seguenti informazioni e restituiscile in formato JSON.
        Se un'informazione non è presente, lascia il campo come null.
        Se il testo non descrive un evento, restituisci un JSON con il campo "is_evento" impostato su false e tutti gli altri campi a null.
        I campi da estrarre sono:
        - is_evento: (boolean) true se è un evento, altrimenti false.
        - name: (string) Il nome o titolo dell'evento.
        - description: (string) Una breve descrizione dell'evento, che possa comprendere tutte le informazioni 
            presenti nel testo fornito (escluse quelle già presenti negli altri campi)
        - start_time: (int) Date e ora completa in formato ISO dell'inizio dell'evento. (cerca qualsiasi orario 
            presente nel testo e usalo come data di inizio anche se non specificato, se non presente riporta solo la data)
        - end_time: (int) Timestamp completo di data e ora dell'inizio dell'evento, se specificato.
        - price: (string) Il costo o il prezzo del biglietto, se specificato.
    
        Testo da analizzare:
        """

        try:
            # Combinazione del prompt con il testo dell'utente
            full_prompt = f"{prompt}\n\n---\n\n{testo_input}"

            # Chiamata all'API di Gemini
            response = self.model.generate_content(full_prompt)

            # Pulizia e parsing della risposta JSON
            # A volte il modello potrebbe restituire il JSON all'interno di un blocco di codice markdown
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
            if not (event_dict := json.loads(cleaned_response)).get("is_evento", False):
                return None
            return Event.load_from_google_gemini(event_dict)

        except Exception as e:
            return {"errore": f"Si è verificato un errore durante la chiamata all'API: {e}"}

    def get_events_from_posts(self, posts: list[dict]) -> list[Event]:
        events = []
        for post in posts:
            event_info = self.extrac_event_info(post['text'])
            if event_info:
                events.append(event_info)
        return events

