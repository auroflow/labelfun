<template>
  <v-app-bar app color="primary" dark>
    <v-toolbar-title class="mr-5">{{ name }}</v-toolbar-title>
    <v-btn
      v-for="link in linksPermitted"
      :key="`${link.name}-header-link`"
      text
      rounded
      :to="link.path.length ? link.path : '/'"
    >
      {{ link.meta.displayName }}
    </v-btn>
    <v-spacer></v-spacer>
    <v-btn v-if="user" text rounded :to="{ name: 'profile' }">
      {{ user.name }}
    </v-btn>
    <v-btn v-else text rounded :to="{ name: 'login' }">游客</v-btn>
  </v-app-bar>
</template>

<script>
import { mapState } from 'vuex'

export default {
  props: ['name'],
  computed: {
    links() {
      return this.$router.getRoutes().filter((link) => link.meta.displayName)
    },
    linksPermitted() {
      return this.user
        ? this.links.filter((link) => !link.meta.requiresNoAuth)
        : this.links.filter((link) => !link.meta.requiresAuth)
    },
    ...mapState({
      user: (state) => state.user.current,
    }),
  },
}
</script>

<style scoped></style>
