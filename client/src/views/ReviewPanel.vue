<template>
  <v-app class="grey darken-2">
    <the-message-bar></the-message-bar>

    <v-footer
      app
      class="d-flex justify-center playback-controller"
      dark
      padless
      inset
    >
      <v-tooltip top color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            icon
            width="40"
            height="40"
            v-bind="attrs"
            v-on="on"
            style="position: absolute; left: 0"
            :to="{ name: 'task', params: { id: task_id.toString() } }"
          >
            <v-icon size="25"> mdi-arrow-left-circle </v-icon>
          </v-btn>
        </template>
        <span>返回</span>
      </v-tooltip>

      <v-tooltip top color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            icon
            width="40"
            height="40"
            v-bind="attrs"
            v-on="on"
            :disabled="entity_idx === 0"
            @click="goToEntity(0)"
          >
            <v-icon size="40"> mdi-chevron-double-left </v-icon>
          </v-btn>
        </template>
        <span>第一个</span>
      </v-tooltip>

      <v-tooltip top color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            icon
            width="40"
            height="40"
            v-bind="attrs"
            v-on="on"
            :disabled="entity_idx === 0"
            @click="goToEntity(entity_idx - 1)"
          >
            <v-icon size="40px"> mdi-chevron-left </v-icon>
          </v-btn>
        </template>
        <span>上一个</span>
      </v-tooltip>
      <v-tooltip top color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn tile icon width="40" height="40" v-bind="attrs" v-on="on">
            <v-icon size="40px"> mdi-circle-small </v-icon>
          </v-btn>
        </template>
        <span>{{ entity_idx + 1 }} / {{ task.entity_count }}</span>
      </v-tooltip>
      <v-tooltip top color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            icon
            width="40"
            height="40"
            v-bind="attrs"
            v-on="on"
            :disabled="entity_idx === task.entity_count - 1"
            @click="goToEntity(entity_idx + 1)"
          >
            <v-icon size="40px"> mdi-chevron-right </v-icon>
          </v-btn>
        </template>
        <span>下一个</span>
      </v-tooltip>
      <v-tooltip top color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            icon
            width="40"
            height="40"
            v-bind="attrs"
            v-on="on"
            :disabled="entity_idx === task.entity_count - 1"
            @click="goToEntity(task.entity_count - 1)"
          >
            <v-icon size="40px"> mdi-chevron-double-right </v-icon>
          </v-btn>
        </template>
        <span>最后一个</span>
      </v-tooltip>
    </v-footer>

    <v-main>
      <review-panel-canvas
        :image="imageURL"
        :bboxes="bboxes"
        :labels="labels"
      ></review-panel-canvas>

      <v-card color="rgb(128,128,128, 0.75)" class="playback-controller">
        <v-card-actions>
          <v-tooltip top color="grey darken-3">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                tile
                icon
                width="40"
                height="40"
                v-bind="attrs"
                v-on="on"
                :disabled="currentFrame === 1"
                @click="currentFrame = 1"
              >
                <v-icon size="40"> mdi-skip-backward </v-icon>
              </v-btn>
            </template>
            <span>第一帧</span>
          </v-tooltip>

          <v-tooltip top color="grey darken-3">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                tile
                icon
                width="40"
                height="40"
                v-bind="attrs"
                v-on="on"
                :disabled="currentFrame === 1"
                @click="currentFrame--"
              >
                <v-icon size="40px"> mdi-skip-previous </v-icon>
              </v-btn>
            </template>
            <span>上一帧</span>
          </v-tooltip>
          <v-tooltip top color="grey darken-3">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                tile
                icon
                width="40"
                height="40"
                v-bind="attrs"
                v-on="on"
                @click="playOrStop"
              >
                <v-icon size="40px">
                  {{ playing ? 'mdi-stop' : 'mdi-play' }}
                </v-icon>
              </v-btn>
            </template>
            <span>{{ currentFrame }} / {{ entity.frame_count }}</span>
          </v-tooltip>
          <v-tooltip top color="grey darken-3">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                tile
                icon
                width="40"
                height="40"
                v-bind="attrs"
                v-on="on"
                :disabled="currentFrame === entity.frame_count"
                @click="currentFrame++"
              >
                <v-icon size="40px"> mdi-skip-next </v-icon>
              </v-btn>
            </template>
            <span>下一帧</span>
          </v-tooltip>
          <v-tooltip top color="grey darken-3">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                tile
                icon
                width="40"
                height="40"
                v-bind="attrs"
                v-on="on"
                :disabled="currentFrame === entity.frame_count"
                @click="currentFrame = entity.frame_count"
              >
                <v-icon size="40px"> mdi-skip-forward </v-icon>
              </v-btn>
            </template>
            <span>最后一帧</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>

      <v-card color="rgb(128,128,128, 0.75)" class="review-buttons">
        <v-card-actions>
          <v-btn dark class="red" @click="review('incorrect')">错误</v-btn>
          <v-spacer></v-spacer>
          <v-icon v-if="entity.status === 'unreviewed'" color="grey" size="30">
            mdi-help-circle
          </v-icon>
          <v-icon v-else-if="entity.review === true" color="green" size="30">
            mdi-check-circle
          </v-icon>
          <v-icon v-else color="red" size="30"> mdi-close-circle </v-icon>
          <v-spacer></v-spacer>
          <v-btn dark class="green" @click="review('correct')">正确</v-btn>
        </v-card-actions>
      </v-card>
    </v-main>
  </v-app>
</template>

<script>
import { mapState } from 'vuex'
import store from '@/store'
import TheMessageBar from '@/components/TheMessageBar'
import ReviewPanelCanvas from '@/components/ReviewPanelCanvas'

function fetchTaskAndEntity(task_id, entity_idx, next) {
  store
    .dispatch('task/fetchTask', task_id)
    .then(() => {
      if (store.state.user.user.id !== store.state.task.task.labeler?.id) {
        return Promise.reject({ message: '无标注权限。' })
      } else {
        const entities = store.state.task.task.entities
        if (entity_idx < 0 || entity_idx >= entities.length) {
          return Promise.reject({ message: '任务无此图片或视频。' })
        } else {
          const entity_id = store.state.task.task.entities[entity_idx].id
          return store.dispatch('entity/fetchEntity', entity_id)
        }
      }
    })
    .then(() => {
      next()
    })
    .catch((err) => {
      store.dispatch('message/pushError', err)
    })
}

export default {
  components: { TheMessageBar, ReviewPanelCanvas },
  props: {
    task_id: {
      type: Number,
      required: true,
    },
    entity_idx: {
      type: Number,
      required: true,
    },
  },

  data: () => ({
    currentFrame: 1,
    playing: false,
  }),

  computed: {
    ...mapState({
      baseURL: (state) => state.baseURL,
      task: (state) => state.task.task,
      user: (state) => state.user.user,
      entity: (state) => state.entity.entity,
    }),

    imageURL() {
      if (this.task.type !== 'video_seg') {
        return this.baseURL + this.entity.key
      } else {
        return (
          this.baseURL +
          this.entity.key +
          '-' +
          this.currentFrame.toString().padStart(6, '0')
        )
      }
    },

    bboxes() {
      if (this.task.type === 'image_cls') return null
      else if (this.task.type === 'image_seg') {
        return this.entity.annotation.map((box) => box.bbox)
      } else {
        return this.entity.annotation.map(
          (object) =>
            object.trajectory.find(
              (snapshot) => snapshot.frame_number === this.currentFrame
            )?.bbox
        )
      }
    },

    labels() {
      if (this.task.type === 'image_cls') return this.entity.annotation
      else return this.entity.annotation.map((item) => item.label)
    },
  },

  methods: {
    review(result) {
      return this.$store
        .dispatch('entity/reviewEntity', {
          id: this.entity.id,
          data: {
            review: result,
          },
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '已保存。')
        })
        .catch((err) => {
          this.$store.dispatch('message/pushError', err)
        })
    },

    goToEntity(entity_idx) {
      this.$router.push({
        name: 'review',
        params: {
          task_id: this.task_id.toString(),
          entity_idx: entity_idx.toString(),
        },
      })
    },

    reset() {
      this.dirty = false
    },

    play() {
      this.playing = true
      this.intervalHandler = setInterval(() => {
        if (this.currentFrame === this.entity.frame_count) {
          this.playing = false
          clearInterval(this.intervalHandler)
        } else {
          this.currentFrame++
        }
      }, 100)
    },

    stop() {
      this.playing = false
      clearInterval(this.intervalHandler)
    },

    playOrStop() {
      if (this.playing) this.stop()
      else this.play()
    },
  },

  beforeRouteEnter(to, from, next) {
    fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
  },

  beforeRouteUpdate(to, from, next) {
    if (this.dirty) {
      this.saveChanges().then(() => {
        this.reset()
        fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
      })
    } else {
      this.reset()
      fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
    }
  },
}
</script>

<style scoped>
.review-buttons {
  position: absolute;
  bottom: 50px;
  left: 0;
  right: 0;
  margin-left: auto;
  margin-right: auto;
  width: 200px;
}
.playback-controller {
  position: absolute;
  bottom: 100px;
}
</style>
