<template>
  <div>
    <v-snackbar
      width="400"
      app
      top
      transition="slide-y-transition"
      v-model="messages.length"
      :color="messages.length ? messages[0].type : null"
      timeout="-1"
      :value="true"
    >
      {{ messages.length ? messages[0].text : '' }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="pop">
          <template v-if="count === 1">关闭</template>
          <template v-else-if="count > 1">下一条 ({{ count - 1 }})</template>
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  computed: {
    ...mapState('message', ['messages']),
    ...mapGetters('message', ['count']),
  },
  methods: {
    ...mapActions('message', ['pop']),
  },
}
</script>

<style scoped></style>
