<template>
  <v-container fluid fill-height>
    <v-row class="align-center justify-center">
      <v-col>
        <v-card width="400" class="mx-auto">
          <v-card-text>
            <template v-if="user !== null">Hello, {{ user.name }}!</template>
            <template v-else>Hello, please login!</template>
          </v-card-text>
          <v-card-actions v-if="user !== null">
            <v-btn @click="logout">注销</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'home',
  computed: {
    ...mapState({ user: (state) => state.user.current }),
  },
  methods: {
    ...mapActions('user', ['logout']),
  },
}
</script>
