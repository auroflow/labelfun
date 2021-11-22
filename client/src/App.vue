<template>
  <v-app>
    <nav-bar :name="name"></nav-bar>
    <v-main>
      <message-bar></message-bar>
      <router-view></router-view>
    </v-main>
    <v-footer color="primary lighten-1" padless>
      <v-layout justify-center wrap>
        <v-flex primary lighten-2 py-4 text-center white--text xs12>
          {{ new Date().getFullYear() }} — <strong>{{ name }}</strong>
        </v-flex>
      </v-layout>
    </v-footer>
  </v-app>
</template>

<script>
import MessageBar from '@/components/MessageBar.vue'
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'App',

  data() {
    return {
      name: '乐标网',
    }
  },

  components: { MessageBar, NavBar },
}
</script>
