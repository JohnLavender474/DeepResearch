<template>
  <div id="app">
    <header>
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/research">Research</RouterLink>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
header {
  background-color: #2c3e50;
  padding: 1rem 2rem;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

nav {
  display: flex;
  gap: 2rem;
}

nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}

nav a:hover {
  opacity: 0.7;
}

nav a.router-link-active {
  color: #42b983;
}

main {
  padding: 0 2rem;
  padding-top: 4rem;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
