<template>
  <div class="contact">
    <h1>Pagina Contatti</h1>
    <p>Contattaci compilando il modulo sottostante.</p>
    <form>
      <input type="text" placeholder="Il tuo nome">
      <input type="email" placeholder="La tua email">
      <textarea placeholder="Il tuo messaggio"></textarea>
      <button type="submit">Invia</button>
    </form>
  </div>
</template>

<style scoped>
.contact {
  text-align: center;
}
form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
  margin: auto;
}
</style>
