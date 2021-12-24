<template>
  <v-app>
    <template
      v-if="$route.name.startsWith('label') || $route.name.endsWith('view')"
    >
      <router-view></router-view>
    </template>
    <template v-else-if="$route.name === 'profile'">
      <nav-bar :name="name" :has-drawer="true">></nav-bar>
      <router-view></router-view>
      <the-footer :name="name"></the-footer>
    </template>
    <template v-else>
      <nav-bar :name="name"> </nav-bar>
      <v-main>
        <message-bar></message-bar>
        <router-view></router-view>
      </v-main>
      <the-footer :name="name"></the-footer>
    </template>
  </v-app>
</template>

<script>
import MessageBar from '@/components/TheMessageBar.vue'
import NavBar from '@/components/TheNavBar.vue'
import TheFooter from '@/components/TheFooter.vue'
export default {
  name: 'App',

  data() {
    return {
      name: '乐标网',
    }
  },

  components: { MessageBar, NavBar, TheFooter },
}
</script>

<style>
html {
  overflow-y: auto !important;
}
</style>
