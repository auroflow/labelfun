<template>
  <v-container>
    <v-row>
      <v-col cols="3">
        <div class="sticky">
          <v-sheet color="grey lighten-4" class="pa-4">
            <v-avatar class="mb-4" color="grey darken-1" size="64"></v-avatar>
            <div>欢迎，{{ user.name }}！</div>
            <div class="mt-2"><v-btn @click="logout">注销</v-btn></div>
          </v-sheet>

          <v-divider></v-divider>

          <v-list>
            <v-list-item-group mandatory v-model="activeComponent">
              <v-list-item
                v-for="({ name, text }, index) in links"
                :key="`${name}-sidebar-link`"
                link
                @click="selectComponent(index)"
              >
                <v-list-item-content>
                  <v-list-item-title>{{ text }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </div>
      </v-col>

      <v-col v-if="activeComponent === 0">
        <profile-user-info :user="user"></profile-user-info>
      </v-col>
      <v-col v-else>TODO</v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex'
import ProfileUserInfo from '@/components/ProfileUserInfo.vue'

export default {
  name: 'home',
  components: {
    ProfileUserInfo,
  },
  data() {
    return {
      activeComponent: 0,
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
          name: 'labelled',
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
    ...mapGetters('user', { user: 'getCurrentUser' }),
  },
  methods: {
    selectComponent(index) {
      this.activeComponent = index
    },
    logout() {
      this.$store.dispatch('user/logout')
      this.$store.dispatch('message/push', {
        type: 'success',
        text: '注销成功。',
      })
      this.$router.push({ name: 'home' })
    },
  },
}
</script>

<style scoped>
.sticky {
  position: sticky;
  top: 5em;
}
</style>
