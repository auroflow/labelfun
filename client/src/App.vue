<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title class="mr-5">{{ name }}</v-toolbar-title>
      <v-btn
        v-for="link in links"
        :key="`${link.name}-header-link`"
        text
        rounded
        :to="link.path.length ? link.path : '/'"
      >
        {{ link.name }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn v-if="user" text rounded :to="{ name: 'profile' }">
        {{ user.name }}
      </v-btn>
      <v-btn v-else text rounded :to="{ name: 'login' }">游客</v-btn>
    </v-app-bar>
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
import { mapState } from 'vuex'

export default {
  name: 'App',

  components: { MessageBar },

  data() {
    return {
      name: '乐标网',

      links: [
        {
          path: '/',
          name: '首页',
        },
        {
          path: '/login',
          name: '登录',
        },
        {
          path: '/signup',
          name: '注册',
        },
      ],
    }
  },

  computed: {
    ...mapState({
      user: (state) => state.user.current,
    }),
  },
}
</script>
