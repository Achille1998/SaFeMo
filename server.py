import asyncio
import tornado.web
import os

from handlers.find_places_handler import PLacesAroundHandler

# --- Configurazione ---
PORT = 8080
# La cartella che contiene i file di produzione generati da `npm run build`
BUILD_DIR = os.path.join(os.path.dirname(__file__), "dist")


async def main():
    """
    Coroutine principale che configura e avvia il server.
    """
    # Controlla se la cartella 'dist' esiste
    if not os.path.exists(BUILD_DIR):
        print(f"❌ Errore: La cartella '{BUILD_DIR}' non esiste.")
        print("Esegui prima `npm run build` per compilare il tuo progetto Vue.")
        return

    app = tornado.web.Application([
        # La gestione dei file statici è già altamente ottimizzata e non
        # richiede modifiche per funzionare in un contesto asincrono.
        (r"/api/placesAround", PLacesAroundHandler),

        (r"/(.*)", tornado.web.StaticFileHandler, {"path": BUILD_DIR, "default_filename": "index.html"}),
    ])

    try:
        ssl_options = {
            "certfile": os.path.join(os.path.dirname(__file__), "server.crt"),
            "keyfile": os.path.join(os.path.dirname(__file__), "server.key"),
        }

        # Crea un server HTTPS
        http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
        http_server.listen(PORT)

    except FileNotFoundError:
        print("\n⚠️  Certificato SSL non trovato. Avvio del server in modalità HTTP (insicura).")
        print("⚠️  La geolocalizzazione potrebbe non funzionare su altri dispositivi.")
        print("   Esegui 'openssl req ...' per generare i certificati.\n")
        app.listen(PORT)

    print(f"✅ Server avviato su https://localhost:{PORT}")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
