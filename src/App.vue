<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">Chi Siamo</RouterLink>
        <RouterLink to="/contact">Contatti</RouterLink>
        <RouterLink to="/placesAround">Locali Vicini</RouterLink>
      </nav>
    </div>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
  padding: 2rem;
  border-bottom: 1px solid #ddd;
}

nav {
  width: 100%;
  font-size: 1rem;
  text-align: center;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

nav a.router-link-exact-active {
  color: hsla(160, 100%, 37%, 1);
}

main {
  padding: 2rem;
}
</style>
