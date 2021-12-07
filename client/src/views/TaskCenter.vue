<template>
  <v-container mt-5>
    <p class="display-1">任务中心</p>
  </v-container>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  data() {
    return {}
  },

  computed: {
    ...mapState('task', ['tasks']),
    ...mapGetters('task', {
      unlabeledTasks: 'getUnlabeledTasks',
      unreviewedTasks: 'getUnreviewedTasks',
      doneTasks: 'getDoneTasks',
    }),
  },
}
</script>
