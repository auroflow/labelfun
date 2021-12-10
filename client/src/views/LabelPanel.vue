<template>
  <v-app>
    <v-navigation-drawer
      :value="true"
      app
      stateless
      dark
      mini-variant
      mini-variant-width="50"
    >
      <v-btn tile block text max-width="10" height="50">
        <v-icon size="30" class="">mdi-arrow-left-circle</v-icon>
      </v-btn>
    </v-navigation-drawer>

    <v-navigation-drawer :value="true" app right width="300" dark stateless>
      <v-list-item>
        <v-list-item-title class="text-center">选框信息</v-list-item-title>
      </v-list-item>
      <v-list-item>
        <v-list-item-title class="text-center"
          >({{ clientX }}, {{ clientY }})</v-list-item-title
        >
      </v-list-item>
    </v-navigation-drawer>

    <v-main>
      <v-sheet
        id="canvas"
        height="100vh"
        class="grey darken-2"
        @mousedown="startDragImage"
        @mousemove.prevent="
          dragImage($event)
          updateCursorLocation($event)
        "
        @mouseup="finishDragImage"
        @wheel="resizeImage"
      >
        <img
          ref="image"
          id="image"
          alt="image"
          draggable="true"
          :src="baseURL + entity.key"
          :style="imgStyle"
        />
      </v-sheet>
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
    dragging: false,
    imgWidth: 100,
    imgLeft: 100,
    imgTop: 50,
    cursorStartX: null,
    cursorStartY: null,
    clientX: null,
    clientY: null,
  }),
  computed: {
    ...mapState({
      baseURL: (state) => state.baseURL,
      task: (state) => state.task.task,
      user: (state) => state.user.user,
      entity: (state) => state.entity.entity,
    }),
    ratio() {
      return this.$refs.image.naturalWidth / this.$refs.image.naturalHeight
    },
    imgStyle() {
      return {
        position: 'absolute',
        width: this.imgWidth + 'px',
        left: this.imgLeft + 'px',
        top: this.imgTop + 'px',
      }
    },
  },
  methods: {
    updateCursorLocation(e) {
      this.clientX = e.clientX - 50
      this.clientY = e.clientY
    },
    startDragImage(event) {
      this.dragging = true
      this.cursorStartX = event.clientX
      this.cursorStartY = event.clientY
    },
    dragImage(e) {
      if (this.dragging) {
        // calculate the new cursor position:
        const cursorDX = e.clientX - this.cursorStartX
        const cursorDY = e.clientY - this.cursorStartY
        this.cursorStartX = e.clientX
        this.cursorStartY = e.clientY
        // set the element's new position:
        this.imgLeft += cursorDX
        this.imgTop += cursorDY
      }
    },
    finishDragImage() {
      this.dragging = false
    },
    resizeImage(event) {
      this.imgWidth += event.deltaY * -0.2
    },
  },
  beforeRouteEnter(to, from, next) {
    fetchTaskAndCheckIdentity(to.params.id, next)
  },
  beforeRouteUpdate(to, from, next) {
    fetchTaskAndCheckIdentity(to.params.id, next)
  },
}
</script>

<style scoped>
#canvas {
  overflow: hidden;
  position: relative;
}
</style>
