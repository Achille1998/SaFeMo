<template>
  <div class="venues-page">
    <h1>Trova Locali nelle Vicinanze</h1>

    <div class="slider-container">
      <label for="radius-slider">Raggio di ricerca: <strong>{{ searchRadius }} km</strong></label>
      <input 
        type="range" 
        id="radius-slider"
        min="1" 
        max="10" 
        step="0.5"
        v-model="searchRadius"
        :disabled="isLoading"
      />
    </div>
    <button @click="findVenues" :disabled="isLoading">
      {{ isLoading ? 'Ricerca in corso...' : 'Trova Locali Qui!' }}
    </button>

    <p v-if="locationError" class="error-message">
      Errore di geolocalizzazione: {{ locationError }}
      <br>Assicurati di aver permesso l'accesso alla posizione.
    </p>

    <div v-if="venues.length > 0" class="venues-list">
      <h2>Risultati della Ricerca</h2>
      <div v-for="venue in venues" :key="venue.name" class="venue-card">
        <h3>{{ venue.name }}</h3>
        <p><strong>Indirizzo:</strong> {{ venue.address }}</p>
        <p><strong>Valutazione:</strong> {{ venue.rating }} ⭐</p>
        <p><strong>Tipo:</strong> <span v-for="(type, index) in venue.type" :key="type">{{ type }}{{ index < venue.type.length - 1 ? ', ' : '' }}</span></p>
        <p v-if="venue.instagram_URL">
          <a :href="venue.instagram_URL" target="_blank" rel="noopener noreferrer">Instagram</a>
        </p>

        <div v-if="venue.events && venue.events.length > 0">
          <h4 @click="toggleEvents(venue.name)" class="events-toggle">
            Eventi ({{ venue.events.length }}) 
            <span class="toggle-icon">{{ expandedVenues[venue.name] ? '▲' : '▼' }}</span>
          </h4>
          <ul v-if="expandedVenues[venue.name]" class="events-list">
            <li v-for="(event, index) in venue.events" :key="index">
              <strong>{{ event.name }}</strong> ({{ event.date }})
              <p>{{ event.description }}</p>
            </li>
          </ul>
        </div>
        <p v-else>Nessun evento in programma.</p>
      </div>
    </div>
    <p v-else-if="!isLoading && !locationError">Premi il pulsante per trovare locali!</p>
    <p v-else-if="isLoading">Caricamento locali...</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const venues = ref([]);
const isLoading = ref(false);
const locationError = ref<string | null>(null);
const expandedVenues = ref({}); // Per tenere traccia degli eventi espansi per ogni locale
const searchRadius = ref(2.5); // Valore iniziale di 2.5 km
const findVenues = async () => {
  isLoading.value = true;
  locationError.value = null;
  venues.value = []; // Pulisci i risultati precedenti

  // Carate Brianza coordinates as default/fallback
  const defaultLat = 45.6983; // Example: Latitude for Carate Brianza
  const defaultLon = 9.2144; // Example: Longitude for Carate Brianza

  try {
    let lat = defaultLat;
    let lon = defaultLon;

    if (navigator.geolocation) {
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0,
        });
      });
      lat = position.coords.latitude;
      lon = position.coords.longitude;
    } else {
      locationError.value = "La geolocalizzazione non è supportata dal tuo browser. Verranno usate le coordinate di Carate Brianza.";
      console.warn("Geolocation not supported, using default coordinates for Carate Brianza.");
    }

    const response = await fetch(`/api/placesAround?lat=${lat}&lon=${lon}&radius=${searchRadius.value}`);
    if (!response.ok) {
      throw new Error(`Errore HTTP: ${response.status}`);
    }
    const r = await response.json();
    venues.value = r.places || [];
    console.log("Dati ricevuti:", venues.value);

  } catch (error) {
    locationError.value = error.message;
    console.error("Errore durante la richiesta dei locali:", error);
  } finally {
    isLoading.value = false;
  }
};

const toggleEvents = (venueName) => {
  expandedVenues.value[venueName] = !expandedVenues.value[venueName];
};
</script>

<style scoped>
.venues-page {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h1 {
  color: #333;
  margin-bottom: 1.5rem;
}

button {
  background-color: #4CAF50;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: background-color 0.3s ease;
  margin-bottom: 1.5rem;
}

button:hover:not(:disabled) {
  background-color: #45a049;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #d9534f;
  background-color: #f2dede;
  border: 1px solid #ebccd1;
  padding: 10px;
  border-radius: 4px;
  margin-top: 1rem;
}

.venues-list {
  margin-top: 2rem;
  text-align: left;
}

.venue-card {
  background-color: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
}

.venue-card h3 {
  color: #007bff;
  margin-top: 0;
  margin-bottom: 0.8rem;
}

.venue-card p {
  margin-bottom: 0.5rem;
  color: #555;
}

.venue-card a {
  color: #007bff;
  text-decoration: none;
}

.venue-card a:hover {
  text-decoration: underline;
}

.events-toggle {
  cursor: pointer;
  color: #6c757d;
  font-weight: bold;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 5px;
}

.events-toggle:hover {
  color: #495057;
}

.toggle-icon {
  font-size: 0.8em;
  line-height: 1;
}

.events-list {
  list-style-type: none;
  padding-left: 0;
  border-top: 1px solid #eee;
  padding-top: 1rem;
  margin-top: 1rem;
}

.events-list li {
  background-color: #f1f1f1;
  border-radius: 5px;
  padding: 0.8rem;
  margin-bottom: 0.7rem;
  border-left: 3px solid #007bff;
}

.events-list li strong {
  color: #333;
}
</style>