<template>
  <v-app>
    <template v-if="$route.name !== 'label'">
      <nav-bar :name="name"></nav-bar>
      <v-main>
        <message-bar></message-bar>
        <router-view></router-view>
      </v-main>
      <the-footer :name="name"></the-footer>
    </template>
    <template v-else>
      <router-view></router-view>
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
