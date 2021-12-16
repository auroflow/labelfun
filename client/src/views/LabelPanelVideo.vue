<template>
  <v-app class="grey darken-2">
    <the-message-bar></the-message-bar>
    <v-navigation-drawer
      :value="true"
      app
      stateless
      dark
      mini-variant
      mini-variant-width="50px"
      @mousemove.prevent
    >
      <!-- Go back -->
      <v-tooltip right color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            block
            icon
            width="50"
            height="50"
            v-bind="attrs"
            v-on="on"
            :disabled="canvasDrawing"
            :to="{ name: 'task', params: { id: task_id.toString() } }"
          >
            <v-icon dark size="30"> mdi-arrow-left-circle </v-icon>
          </v-btn>
        </template>
        <span>返回</span>
      </v-tooltip>

      <!-- Add object -->
      <v-tooltip right color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            block
            icon
            max-width="10"
            height="50"
            v-bind="attrs"
            v-on="on"
            :disabled="canvasDrawing"
            @click="toggleLabelChooser"
          >
            <v-icon dark size="30"> mdi-tag-plus </v-icon>
          </v-btn>
        </template>
        <span>添加物体</span>
      </v-tooltip>

      <template v-slot:append>
        <!-- First entity -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              v-bind="attrs"
              v-on="on"
              :disabled="entity_idx === 0 || canvasDrawing"
              @click="goToEntity(0)"
            >
              <v-icon dark size="30"> mdi-chevron-double-up </v-icon>
            </v-btn>
          </template>
          <span>第一个</span>
        </v-tooltip>

        <!-- Previous entity -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              v-bind="attrs"
              v-on="on"
              :disabled="entity_idx === 0 || canvasDrawing"
              @click="goToEntity(entity_idx - 1)"
            >
              <v-icon dark size="30"> mdi-chevron-up </v-icon>
            </v-btn>
          </template>
          <span>上一个</span>
        </v-tooltip>

        <!-- This count -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon dark size="30"> mdi-circle-small </v-icon>
            </v-btn>
          </template>
          <span>{{ entity_idx + 1 }} / {{ task.entities.length }}</span>
        </v-tooltip>

        <!-- Next entity -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              :disabled="
                entity_idx === task.entities.length - 1 || canvasDrawing
              "
              v-bind="attrs"
              v-on="on"
              @click="goToEntity(entity_idx + 1)"
            >
              <v-icon dark size="30"> mdi-chevron-down </v-icon>
            </v-btn>
          </template>
          <span>下一个</span>
        </v-tooltip>

        <!-- Last entity -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              :disabled="
                entity_idx === task.entities.length - 1 || canvasDrawing
              "
              v-bind="attrs"
              v-on="on"
              @click="goToEntity(task.entities.length - 1)"
            >
              <v-icon dark size="30"> mdi-chevron-double-down </v-icon>
            </v-btn>
          </template>
          <span>最后一个</span>
        </v-tooltip>

        <!-- Save -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              v-bind="attrs"
              v-on="on"
              :disabled="canvasDrawing"
              @click="saveChanges"
            >
              <v-icon dark size="30"> mdi-content-save </v-icon>
            </v-btn>
          </template>
          <span>保存</span>
        </v-tooltip>
      </template>
    </v-navigation-drawer>

    <v-navigation-drawer
      :value="true"
      app
      right
      width="300px"
      dark
      stateless
      @mousemove.prevent
    >
      <v-list-item>
        <v-list-item-title class="text-center">物体信息</v-list-item-title>
      </v-list-item>
      <transition-group name="v-expand-transition">
        <div
          v-for="(object, index) in entity.annotation"
          :key="index"
          class="mx-4"
        >
          <v-alert
            border="left"
            :color="object === chosenObject ? 'green darken-2' : 'green'"
            class="label-selector"
            dark
            dense
            transition="v-expand-transition"
            @click="chooseBox(index)"
            v-click-outside="{
              handler: unchooseBox,
              include: getIncludedElements,
            }"
          >
            <v-chip
              :color="object === chosenObject ? 'green' : 'green lighten-2'"
              class="mr-2"
              >{{ object.label }}</v-chip
            >
            <template v-slot:append>
              <template v-if="!boxInThisFrame(object)">
                <v-tooltip bottom color="grey darken-3">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      @click="startDrawing(object)"
                      v-bind="attrs"
                      v-on="on"
                      :disabled="canvasDrawing"
                    >
                      <v-icon class="mr-1">mdi-plus-circle-outline</v-icon>
                    </v-btn>
                  </template>
                  <span>在此帧上标注该物体</span>
                </v-tooltip>
              </template>
              <template v-else>
                <v-tooltip bottom color="grey darken-3">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      @click="deleteBox(object)"
                      v-bind="attrs"
                      v-on="on"
                      :disabled="canvasDrawing"
                    >
                      <v-icon>mdi-close-circle</v-icon>
                    </v-btn>
                  </template>
                  <span>删除该帧上的标注</span>
                </v-tooltip>
              </template>
              <template v-if="object.trajectory.length === 0">
                <v-tooltip bottom color="grey darken-3">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      @click="deleteObject(object)"
                      v-bind="attrs"
                      v-on="on"
                      :disabled="canvasDrawing"
                    >
                      <v-icon>mdi-close-box</v-icon>
                    </v-btn>
                  </template>
                  <span>删除该物体</span>
                </v-tooltip>
              </template>
            </template>
          </v-alert>
        </div>
      </transition-group>
    </v-navigation-drawer>

    <v-footer
      app
      color="grey darken-3"
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
            :disabled="canvasDrawing || current_frame === 1"
            @click="current_frame = 1"
          >
            <v-icon size="40"> mdi-chevron-double-left </v-icon>
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
            :disabled="current_frame === 1"
            @click="current_frame--"
          >
            <v-icon size="40px"> mdi-chevron-left </v-icon>
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
            :disabled="canvasDrawing"
          >
            <v-icon size="40px"> mdi-play </v-icon>
          </v-btn>
        </template>
        <span>{{ current_frame }} / {{ entity.frame_count }}</span>
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
            :disabled="canvasDrawing || current_frame === entity.frame_count"
            @click="current_frame++"
          >
            <v-icon size="40px"> mdi-chevron-right </v-icon>
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
            :disabled="canvasDrawing || current_frame === entity.frame_count"
            @click="current_frame = entity.frame_count"
          >
            <v-icon size="40px"> mdi-chevron-double-right </v-icon>
          </v-btn>
        </template>
        <span>最后一帧</span>
      </v-tooltip>
    </v-footer>

    <v-main>
      <v-sheet
        style="z-index: 100"
        v-show="showLabels"
        elevation="10"
        rounded="xl"
        width="300"
        id="label-chooser"
        @mouseover="inLabelChooser = true"
        @mouseout="inLabelChooser = false"
      >
        <v-sheet class="pa-2 grey darken-3" dark rounded="t-xl">
          <v-container>
            <v-row>
              <p class="text-body-1 my-auto mx-2">选择标签</p>
              <v-spacer></v-spacer>
              <v-btn icon @click="closeAndClearLabelChooser">
                <v-icon>mdi-close</v-icon>
              </v-btn>
              <v-btn
                class="ml-2"
                icon
                @click="addObject"
                :disabled="canvasDrawing || label === -1"
              >
                <v-icon>mdi-check</v-icon>
              </v-btn>
            </v-row>
          </v-container>
        </v-sheet>

        <v-sheet class="pa-4" rounded="b-xl">
          <v-chip-group active-class="grey" v-model="label" column>
            <v-chip v-for="tag in task.labels" class="" :key="tag">
              {{ tag }}
            </v-chip>
          </v-chip-group>
        </v-sheet>
      </v-sheet>

      <label-panel-canvas
        :in-label-chooser="inLabelChooser"
        :image="entity"
        :url="imgURL"
        :objects="entity.annotation"
        :current-frame="current_frame"
        :canvas-drawing="canvasDrawing"
        :chosen-box="getChosenBox"
        :is-video="true"
        @new-box-drawn="addNewBox"
        @choose-box="chooseBox($event)"
        @resize-box="resizeBox"
      ></label-panel-canvas>
    </v-main>
  </v-app>
</template>

<script>
import store from '@/store'
import { mapState } from 'vuex'
import TheMessageBar from '@/components/TheMessageBar'
import LabelPanelCanvas from '@/components/LabelPanelCanvas'

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
  components: {
    TheMessageBar,
    LabelPanelCanvas,
  },
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
    current_frame: 1,
    dirty: false,
    label: -1, // chosen label index
    showLabels: false, // whether the label chooser is shown
    inLabelChooser: false, // whether the cursor is in label chooser
    chosenObject: null,
    canvasDrawing: false,
  }),
  computed: {
    ...mapState({
      baseURL: (state) => state.baseURL,
      task: (state) => state.task.task,
      user: (state) => state.user.user,
      entity: (state) => state.entity.entity,
    }),
    imgURL() {
      return (
        this.baseURL +
        this.entity.key +
        '-' +
        this.current_frame.toString().padStart(6, '0')
      )
    },
    getChosenBox() {
      return this.chosenObject?.trajectory.find(
        (snapshot) => snapshot.frame_number === this.current_frame
      )?.bbox
    },
  },
  methods: {
    chooseBox(index) {
      console.log('choosing', this.entity.annotation[index])
      this.chosenObject = this.entity.annotation[index]
    },

    unchooseBox() {
      if (!this.canvasDrawing) this.chosenObject = null
    },

    getIncludedElements() {
      return [
        ...document.getElementsByClassName('label-selector'),
        ...document.getElementsByClassName('playback-controller'),
      ]
    },

    closeAndClearLabelChooser() {
      this.label = -1
      this.drawing = 0
      this.showLabels = false
    },

    toggleLabelChooser() {
      this.drawing = 0
      if (this.showLabels) {
        this.closeAndClearLabelChooser()
      } else {
        this.showLabels = true
      }
    },

    addObject() {
      this.$store.dispatch('entity/addObject', this.task.labels[this.label])
      this.showLabels = false
      this.label = -1
    },

    boxInThisFrame(object) {
      return object.trajectory.find(
        (snapshot) => snapshot.frame_number === this.current_frame
      )
    },

    startDrawing() {
      this.canvasDrawing = true
    },

    addNewBox(bbox) {
      this.dirty = true
      this.canvasDrawing = false

      if (bbox) {
        const payload = {
          object: this.chosenObject,
          snapshot: {
            frame_number: this.current_frame,
            bbox: bbox,
          },
        }
        console.log(payload)
        this.$store.dispatch('entity/addBoxToObject', payload)
      }
    },

    resizeBox(e) {
      this.dirty = true
      this.$store.dispatch('entity/resizeBoxInObject', {
        ...e,
        frame_number: this.current_frame,
      })
    },

    deleteBox(object) {
      this.dirty = true
      const payload = {
        object: object,
        frame_number: this.current_frame,
      }
      this.$store.dispatch('entity/deleteBoxInFrame', payload)
    },

    deleteObject(object) {
      this.dirty = true
      this.$store.dispatch('entity/deleteObject', object)
    },

    saveChanges() {
      return this.$store
        .dispatch('entity/labelEntity', {
          id: this.entity.id,
          data: {
            objects: this.entity.annotation,
          },
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '已保存修改。')
        })
        .catch((err) => {
          this.$store.dispatch('message/pushError', err)
        })
    },

    goToEntity(entity_idx) {
      this.$router.push({
        name: 'label-vid',
        params: {
          task_id: this.task_id.toString(),
          entity_idx: entity_idx.toString(),
        },
      })
    },

    reset() {
      this.dirty = false
      this.label = -1 // chosen label index
      this.showLabels = false // whether the label chooser is shown
      this.inLabelChooser = false // whether the cursor is in label chooser
      this.chosenObject = null
      this.canvasDrawing = false
      this.current_frame = 1
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
#canvas {
  overflow: hidden;
  position: relative;
}
#label-chooser {
  position: absolute;
  top: 50px;
  left: 5px;
  z-index: 1;
}
.vl {
  position: absolute;
  border-left-width: 1px;
  border-left-color: red;
  height: 100%;
  z-index: 100;
}
.hl {
  position: absolute;
  border-top-width: 1px;
  border-top-color: red;
  width: 100%;
  z-index: 100;
}
.new-box {
  position: absolute;
  border-color: yellowgreen;
  border-width: 2px;
}
.box {
  position: absolute;
  border-color: yellowgreen;
  border-width: 2px;
}
</style>
