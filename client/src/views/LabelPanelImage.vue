<template>
  <v-app class="grey darken-2">
    <v-fade-transition>
      <v-overlay
        class="text-center"
        v-model="$vuetify.breakpoint.smAndDown"
        z-index="10000"
      >
        <p class="text-body-1">请在电脑端操作或放大窗口</p>
        <v-btn
          class="success"
          :to="{ name: 'task', params: { id: task_id.toString() } }"
        >
          返回
        </v-btn>
      </v-overlay>
    </v-fade-transition>
    <the-message-bar></the-message-bar>

    <!-- Left nav -->
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

      <!-- Add box -->
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
            :disabled="canvasDrawing || entity.status === 'done'"
            @click="toggleLabelChooser"
          >
            <v-icon dark size="30"> mdi-vector-square-plus </v-icon>
          </v-btn>
        </template>
        <span>添加选框</span>
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

    <!-- right nav -->
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
        <v-list-item-title class="text-center">选框信息</v-list-item-title>
      </v-list-item>
      <transition-group name="v-expand-transition">
        <div
          v-for="(box, index) in entity.annotation"
          :key="index"
          class="mx-4"
        >
          <v-alert
            border="left"
            :color="box === chosenBox ? 'green darken-2' : 'green'"
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
              :color="box === chosenBox ? 'green' : 'green lighten-2'"
              class="mr-2"
              >{{ box.label }}</v-chip
            >
            <template v-slot:append>
              <v-icon v-if="entity.status !== 'done'" @click="deleteBox(box)"
                >mdi-close-circle</v-icon
              >
            </template>
          </v-alert>
        </div>
      </transition-group>
    </v-navigation-drawer>

    <v-main>
      <v-dialog-transition>
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
                  @click="startDrawing"
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
      </v-dialog-transition>

      <v-hover>
        <template>
          <label-panel-canvas
            :in-label-chooser="inLabelChooser"
            :image="entity"
            :boxes="entity.annotation"
            :canvas-drawing="canvasDrawing"
            :chosen-box="getChosenBox"
            @new-box-drawn="addNewBox"
            @choose-box="chooseBox"
            @resize-box="resizeBox"
          >
            <v-fade-transition>
              <v-overlay
                v-if="entity.status === 'done'"
                v-model="showOverlay"
                absolute
                color="#f0ffff"
                z-index="1000"
              >
                <v-container>
                  <v-row justify="center">
                    <v-icon
                      color="green darken-3"
                      x-large
                      @click="showOverlay = false"
                    >
                      mdi-check-circle
                    </v-icon>
                  </v-row>
                  <v-row justify="center">
                    <p
                      class="text-body-1 font-weight-bold green--text text--darken-3"
                    >
                      已完成
                    </p>
                  </v-row>
                </v-container>
              </v-overlay>
            </v-fade-transition>
          </label-panel-canvas>
        </template>
      </v-hover>
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
    dirty: false,
    label: -1, // chosen label index
    showLabels: false, // whether the label chooser is shown
    inLabelChooser: false, // whether the cursor is in label chooser
    chosenBox: null,
    canvasDrawing: false,
    showOverlay: true,
  }),
  computed: {
    ...mapState({
      baseURL: (state) => state.baseURL,
      task: (state) => state.task.task,
      user: (state) => state.user.user,
      entity: (state) => state.entity.entity,
    }),
    getChosenBox() {
      return this.chosenBox?.bbox
    },
  },
  methods: {
    chooseBox(index) {
      if (!this.canvasDrawing) this.chosenBox = this.entity.annotation[index]
    },

    unchooseBox() {
      if (!this.canvasDrawing) this.chosenBox = null
    },

    getIncludedElements() {
      return [...document.getElementsByClassName('label-selector')]
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

    startDrawing() {
      this.canvasDrawing = true
      this.showLabels = false
    },

    addNewBox(bbox) {
      this.dirty = true
      this.canvasDrawing = false
      const labelChosen = this.label
      this.label = -1
      if (bbox) {
        const box = {
          label: this.task.labels[labelChosen],
          bbox: bbox,
        }
        this.$store.dispatch('entity/addBox', box)
      }
    },

    resizeBox(e) {
      this.dirty = true
      this.$store.dispatch('entity/resizeBox', e)
    },

    deleteBox(box) {
      if (box && this.entity.status !== 'done') {
        this.dirty = true
        this.$store.dispatch('entity/deleteBox', box)
      }
    },

    saveChanges() {
      return this.$store
        .dispatch('entity/labelEntity', {
          id: this.entity.id,
          data: {
            boxes: this.entity.annotation,
          },
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '已保存修改。')
        })
    },

    goToEntity(entity_idx) {
      this.$router.push({
        name: 'label-img',
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
      this.chosenBox = null
      this.canvasDrawing = false
      this.showOverlay = true
    },
  },
  mounted() {
    window.addEventListener('keyup', (event) => {
      if (event.key === 'Delete' && this.chosenBox) {
        this.deleteBox(this.chosenBox)
      } else if (event.key === 'Enter') {
        this.showOverlay = false
      }
    })
  },
  beforeRouteEnter(to, from, next) {
    fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
  },
  beforeRouteUpdate(to, from, next) {
    if (this.dirty) {
      this.saveChanges().finally(() => {
        this.reset()
        fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
      })
    } else {
      this.reset()
      fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
    }
  },
  beforeRouteLeave(to, from, next) {
    if (this.dirty) {
      this.saveChanges().then(() => next())
    } else next()
  },
}
</script>

<style scoped>
#label-chooser {
  position: absolute;
  top: 50px;
  left: 5px;
  z-index: 1;
}
</style>
