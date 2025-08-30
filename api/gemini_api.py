import google.generativeai as genai
import json
import os
# Configura la tua chiave API di Gemini
# NOTA: Per maggiore sicurezza, si consiglia di gestire la chiave API
# tramite variabili d'ambiente o altri sistemi di gestione dei secret.
try:
    genai.configure(api_key="LA_TUA_CHIAVE_API")
except Exception as e:
    print(f"Errore nella configurazione dell'API: {e}")
    exit()


def estrai_informazioni_evento(testo_input):
    """
    Analizza un testo per estrarre informazioni su un evento utilizzando l'API Gemini.

    Args:
        testo_input (str): Il testo da analizzare.

    Returns:
        dict: Un dizionario contenente le informazioni sull'evento estratte,
              o un messaggio di errore.
    """
    # Configurazione del modello
    # Usiamo 'gemini-1.5-flash-latest' per ottimizzare i costi e la velocità.
    # La temperatura è impostata a 0 per ottenere risposte più deterministiche.
    generation_config = {
        "temperature": 0.0,
        "response_mime_type": "application/json",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        generation_config=generation_config,
    )

    # Istruzioni per il modello
    # Definiamo chiaramente il compito e il formato di output desiderato.
    prompt = """
    Analizza il testo fornito e determina se descrive un evento.
    Se il testo descrive un evento, estrai le seguenti informazioni e restituiscile in formato JSON.
    Se un'informazione non è presente, lascia il campo come null.
    Se il testo non descrive un evento, restituisci un JSON con il campo "is_evento" impostato su false e tutti gli altri campi a null.

    I campi da estrarre sono:
    - is_evento: (boolean) true se è un evento, altrimenti false.
    - nome_evento: (string) Il nome o titolo dell'evento.
    - descrizione: (string) Una breve descrizione dell'evento.
    - data: (string) La data dell'evento.
    - ora_inizio: (string) L'ora di inizio, se specificata.
    - ora_fine: (string) L'ora di fine, se specificata.
    - costo: (string) Il costo o il prezzo del biglietto, se specificato.
    - luogo: (string) Il luogo dove si svolge l'evento.

    Testo da analizzare:
    """

    try:
        # Combinazione del prompt con il testo dell'utente
        full_prompt = f"{prompt}\n\n---\n\n{testo_input}"

        # Chiamata all'API di Gemini
        response = model.generate_content(full_prompt)

        # Pulizia e parsing della risposta JSON
        # A volte il modello potrebbe restituire il JSON all'interno di un blocco di codice markdown
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        return json.loads(cleaned_response)

    except Exception as e:
        return {"errore": f"Si è verificato un errore durante la chiamata all'API: {e}"}


# --- Esempio di utilizzo ---
if __name__ == "__main__":
    testo_di_esempio = """
    🗓Venerdì 6 Giugno PRO LOCO MONTECCHIA presenta:
    🌟ＡＦＲＯ ＶＩＢＥＳ ＳＵＭＭＥＲ ＴＯＵＲ ２０２５🌟
    Unisciti a noi per una serata magica,dove il ritmo incontrerà la bellezza del cielo stellato!
    📍Luogo: Piazza Umberto I, 37030 Montecchia di Crosara (Vr)
    🍝🍔 Ricco stand gastronomico DALLE 22.00
    🎧DJ Morgan
    🎙Andrea Meggio
    Preparatevi a ballare, a divertirvi e vivere una notte indimenticabile sotto le stelle.
    Non mancate!🌟❤️
    """

    informazioni_estratte = estrai_informazioni_evento(testo_di_esempio)

    # Stampa dei risultati in un formato leggibile
    print("--- Risultati dell'Estrazione ---")
    print(json.dumps(informazioni_estratte, indent=4, ensure_ascii=False))
    print("---------------------------------")

    # Esempio con un testo che non è un evento
    testo_non_evento = "Questa è una ricetta per una deliziosa torta al cioccolato. Avrai bisogno di farina, zucchero e cacao."

    print("\n--- Analisi di un testo non relativo a un evento ---")
    informazioni_non_evento = estrai_informazioni_evento(testo_non_evento)
    print(json.dumps(informazioni_non_evento, indent=4, ensure_ascii=False))
    print("--------------------------------------------------")