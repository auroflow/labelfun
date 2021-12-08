<template>
  <v-container mt-5>
    <p class="display-1">任务中心</p>
    <v-tabs v-model="tab">
      <v-tab v-for="(tabItem, index) in tabItems" :key="`${index}-tab-name`">
        {{ tabItem.title }}
      </v-tab>
    </v-tabs>

    <v-tabs-items v-model="tab">
      <v-tab-item
        v-for="(tabItem, index) in tabItems"
        :key="`${index}-tab-index`"
      >
        <task-list :tasks="tabItem.content"></task-list>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import store from '@/store'
import TaskList from '@/components/BaseTaskList'

function fetchTasks(next) {
  store.dispatch('task/fetchTasks').then(() => {
    next()
  })
}

export default {
  components: { TaskList: TaskList },
  data() {
    return {
      tab: null,
    }
  },

  computed: {
    ...mapState('task', ['tasks']),
    ...mapGetters('task', {
      unlabeledTasks: 'getUnlabeledTasks',
      unreviewedTasks: 'getUnreviewedTasks',
      doneTasks: 'getDoneTasks',
    }),
    tabItems() {
      return [
        { title: '未标注', content: this.unlabeledTasks },
        { title: '未审核', content: this.unreviewedTasks },
        { title: '已完成', content: this.doneTasks },
      ]
    },
  },

  beforeRouteEnter(routeTo, routeFrom, next) {
    fetchTasks(next)
  },
}
</script>
