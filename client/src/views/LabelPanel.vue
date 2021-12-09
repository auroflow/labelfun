<template>
  <v-app class="grey darken-2">
    <v-navigation-drawer
      :value="true"
      app
      stateless
      dark
      mini-variant
      mini-variant-width="50"
    >
    </v-navigation-drawer>

    <v-navigation-drawer :value="true" app right width="300" dark stateless>
    </v-navigation-drawer>

    <v-main>
      <v-img :src="baseURL + entity.key"></v-img>
    </v-main>
  </v-app>
</template>

<script>
import store from '@/store'
import { mapState } from 'vuex'

function fetchTaskAndCheckIdentity(id, next) {
  store.dispatch('task/fetchTask', id).then(() => {
    if (store.state.user.user.id !== store.state.task.task.labeler?.id) {
      store.dispatch('message/push', {
        type: 'error',
        text: '无标注权限。',
      })
      next({ name: 'task', params: { id: id.toString() } })
    } else {
      const entity = store.state.task.task.entities[0]
      store.dispatch('entity/fetchEntity', entity.id).then(() => {
        next()
      })
    }
  })
}

export default {
  props: {
    id: {
      type: Number,
      required: true,
    },
  },

  data: () => ({
    index: 0,
  }),
  computed: {
    ...mapState({
      baseURL: (state) => state.baseURL,
      task: (state) => state.task.task,
      user: (state) => state.user.user,
      entity: (state) => state.entity.entity,
    }),
  },
  beforeRouteEnter(to, from, next) {
    fetchTaskAndCheckIdentity(to.params.id, next)
  },
  beforeRouteUpdate(to, from, next) {
    fetchTaskAndCheckIdentity(to.params.id, next)
  },
}
</script>
