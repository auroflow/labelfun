<template>
  <div>
    <v-navigation-drawer app clipped v-model="drawer">
      <v-sheet color="grey lighten-4" class="pa-4">
        <div>欢迎，{{ user.name }}！</div>
        <div class="mt-2">
          <v-btn @click="logout" class="secondary">注销</v-btn>
        </div>
      </v-sheet>

      <v-divider></v-divider>

      <v-tabs v-model="tab" vertical>
        <v-tab
          v-for="{ name, text } in links"
          :key="`${name}-sidebar-link`"
          class="text-center"
        >
          {{ text }}
        </v-tab>
      </v-tabs>
    </v-navigation-drawer>
    <v-main>
      <v-container>
        <v-row>
          <v-col>
            <v-tabs-items v-model="tab">
              <v-tab-item>
                <profile-user-info :user="user"></profile-user-info>
              </v-tab-item>
              <v-tab-item>
                <task-list :tasks="createdBy(user.id)"></task-list>
              </v-tab-item>
              <v-tab-item>
                <task-list :tasks="labeledBy(user.id)"></task-list>
              </v-tab-item>
              <v-tab-item>
                <task-list :tasks="reviewedBy(user.id)"></task-list>
              </v-tab-item>
            </v-tabs-items>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import ProfileUserInfo from '@/components/ProfileUserInfo.vue'
import TaskList from '@/components/BaseTaskList.vue'
import store from '@/store'

function fetchTasks(next) {
  store.dispatch('task/fetchTasks').then(() => {
    next()
  })
}

export default {
  name: 'home',
  components: {
    ProfileUserInfo,
    TaskList,
  },
  data() {
    return {
      tab: null,
      links: [
        {
          name: 'profile',
          text: '个人资料',
        },
        {
          name: 'published',
          text: '我发布的任务',
        },
        {
          name: 'labeled',
          text: '我标注的任务',
        },
        {
          name: 'reviewed',
          text: '我审核的任务',
        },
      ],
    }
  },
  computed: {
    drawer: {
      get() {
        return this.$store.state.drawer
      },
      set(value) {
        this.$store.dispatch('setDrawer', value)
      },
    },
    ...mapGetters({
      user: 'user/getCurrentUser',
      createdBy: 'task/getTasksByCreator',
      labeledBy: 'task/getTasksByLabeler',
      reviewedBy: 'task/getTasksByReviewer',
    }),
  },
  methods: {
    selectComponent(index) {
      this.tab = index
    },
    logout() {
      this.$store.dispatch('user/logout')
      this.$store.dispatch('message/pushSuccess', '注销成功。')
      this.$router.push({ name: 'login' })
    },
  },
  beforeRouteEnter(to, from, next) {
    fetchTasks(next)
  },
}
</script>

<style scoped>
.sticky {
  position: sticky;
  top: 5em;
}
</style>
