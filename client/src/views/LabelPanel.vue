<template>
  <v-app>
    <the-message-bar></the-message-bar>
    <v-navigation-drawer
      :value="true"
      app
      stateless
      dark
      mini-variant
      mini-variant-width="50px"
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
            :to="{ name: 'task', params: { id: id.toString() } }"
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
            @click="toggleLabelChooser"
          >
            <v-icon dark v-bind="attrs" v-on="on" size="30">
              mdi-vector-square-plus
            </v-icon>
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
              :disabled="index === 0"
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
              :disabled="index === 0"
              @click="goToEntity(index - 1)"
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
          <span>{{ index + 1 }} / {{ task.entities.length }}</span>
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
              :disabled="index === task.entities.length - 1"
              v-bind="attrs"
              v-on="on"
              @click="goToEntity(index + 1)"
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
              :disabled="index === task.entities.length - 1"
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
              :to="{ name: 'task', params: { id: id.toString() } }"
            >
              <v-icon dark size="30"> mdi-content-save </v-icon>
            </v-btn>
          </template>
          <span>保存</span>
        </v-tooltip>
      </template>
    </v-navigation-drawer>

    <v-navigation-drawer :value="true" app right width="300px" dark stateless>
      <v-list-item>
        <v-list-item-title class="text-center"
          >({{ clientX }}, {{ clientY }})</v-list-item-title
        >
      </v-list-item>
      <v-list-item>
        <v-list-item-title class="text-center">选框信息</v-list-item-title>
      </v-list-item>
      <v-list-item v-for="(box, index) in boxes" :key="index">
        <v-list-item-title class="text-center"
          >{{ box.label }}: [{{ Number(box.bbox[0]).toFixed(2) }},
          {{ Number(box.bbox[1]).toFixed(2) }},
          {{ Number(box.bbox[2]).toFixed(2) }},
          {{ Number(box.bbox[3]).toFixed(2) }}]</v-list-item-title
        >
      </v-list-item>
    </v-navigation-drawer>

    <v-main>
      <v-sheet
        id="canvas"
        ref="canvas"
        height="100vh"
        class="grey darken-2"
        @mousedown="
          startDragImage($event)
          draw($event)
        "
        @mousemove.prevent="
          dragImage($event)
          updateCursorLocation($event)
        "
        @mouseup="finishDragImage"
        @mouseout="mouseOutOfCanvas"
        @mouseover="mouseOnCanvas"
        @wheel="resizeImage"
      >
        <v-dialog-transition>
          <v-sheet
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
                    :disabled="this.drawing !== 0 || this.label === -1"
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

        <img
          ref="image"
          id="image"
          alt="image"
          draggable="true"
          :src="baseURL + entity.key"
          :style="imgStyle"
          @mousedown="draw"
          @load="adjustImage"
        />

        <div class="vl" :style="vlStyle"></div>
        <div class="hl" :style="hlStyle"></div>
        <div class="new-box" :style="newBoxStyle"></div>
        <label-panel-box
          v-for="(box, index) in boxes"
          :key="index"
          :height="imgHeight"
          :width="imgHeight * ratio"
          :left="imgLeft"
          :top="imgTop"
          :box="box"
        ></label-panel-box>
      </v-sheet>
    </v-main>
  </v-app>
</template>

<script>
import store from '@/store'
import { mapState } from 'vuex'
import LabelPanelBox from '@/components/LabelPanelBox'
import TheMessageBar from '@/components/TheMessageBar'

function fetchTaskAndCheckIdentity(id, to, next) {
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
        to.params.boxes = store.state.entity.entity.annotation
        next()
      })
    }
  })
}

export default {
  components: {
    TheMessageBar,
    LabelPanelBox,
  },
  props: {
    id: {
      type: Number,
      required: true,
    },
  },

  data: () => ({
    dirty: false, // is dirty
    index: 0, // Entity index (in the task.entities array)
    label: -1, // chosen label index
    showLabels: false, // whether the label chooser is shown
    inLabelChooser: false, // whether the cursor is in label chooser
    drawing: 0, // the drawing status. (0 -> not drawing, 1 -> to select 1st point, 2 -> to select 2nd point)
    dragging: false, // whether the user is dragging the image
    rememberDragging: false, // whether the user was dragging the image before cursor left canvas
    ratio: null, // image width / height
    imgHeight: null, // image height
    imgLeft: null, // image "left" css property
    imgTop: null, // image "top" css property
    cursorStartX: null, // cursor location of last mousemove event, recorded when dragging
    cursorStartY: null, // cursor location of last mousemove event, recorded when dragging
    clientX: 0, // cursor location
    clientY: 0, // cursor location
    boxes: [],
    chosenBox: null,
    newBox: {
      x1: 0,
      y1: 0,
    },
  }),
  computed: {
    ...mapState({
      baseURL: (state) => state.baseURL,
      task: (state) => state.task.task,
      user: (state) => state.user.user,
      entity: (state) => state.entity.entity,
    }),
    imgStyle() {
      return {
        position: 'absolute',
        height: this.imgHeight + 'px',
        left: this.imgLeft + 'px',
        top: this.imgTop + 'px',
      }
    },
    vlStyle() {
      return {
        borderLeftStyle: this.drawing ? 'solid' : 'none',
        left: this.clientX + 'px',
      }
    },
    hlStyle() {
      return {
        borderTopStyle: this.drawing ? 'solid' : 'none',
        top: this.clientY + 'px',
      }
    },
    newBoxStyle() {
      return {
        borderStyle: this.drawing === 2 ? 'solid' : 'none',
        left: Math.min(this.clientX, this.newBox.x1) + 'px',
        width: Math.abs(this.clientX - this.newBox.x1) + 'px',
        top: Math.min(this.clientY, this.newBox.y1) + 'px',
        height: Math.abs(this.clientY - this.newBox.y1) + 'px',
      }
    },
  },
  methods: {
    updateCursorLocation(e) {
      this.clientX = e.clientX - 50
      this.clientY = e.clientY
    },
    startDragImage(event) {
      if (!this.inLabelChooser && !this.drawing) {
        this.dragging = true
        this.cursorStartX = event.clientX
        this.cursorStartY = event.clientY
      }
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
    mouseOutOfCanvas() {
      if (this.dragging) {
        this.dragging = false
        this.rememberDragging = true
      }
    },
    mouseOnCanvas(event) {
      if (this.rememberDragging && event.buttons === 1) {
        this.dragging = true
        this.rememberDragging = false
      } else {
        this.rememberDragging = false
      }
    },
    resizeImage(event) {
      if (!this.inLabelChooser) {
        const delta = event.deltaY * -0.0005
        this.imgHeight += this.imgHeight * delta
        this.imgLeft = (1 + delta) * this.imgLeft - delta * this.clientX
        this.imgTop = (1 + delta) * this.imgTop - delta * this.clientY
        this.newBox.x1 = (1 + delta) * this.newBox.x1 - delta * this.clientX
        this.newBox.y1 = (1 + delta) * this.newBox.y1 - delta * this.clientY
      }
    },
    adjustImage() {
      let canvasWidth = document.getElementById('canvas').offsetWidth
      let canvasHeight = document.getElementById('canvas').offsetHeight
      let canvasRatio = canvasWidth / canvasHeight
      this.ratio =
        this.$refs.image.naturalWidth / this.$refs.image.naturalHeight
      if (this.ratio < canvasRatio) {
        this.imgHeight = canvasHeight
      } else {
        this.imgHeight = (canvasHeight * canvasRatio) / this.ratio
      }
      this.imgLeft =
        this.ratio > canvasRatio
          ? 0
          : (canvasWidth - this.imgHeight * this.ratio) / 2
      this.imgTop =
        this.ratio > canvasRatio ? (canvasHeight - this.imgHeight) / 2 : 0
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
      this.showLabels = false
      this.drawing = 1
    },
    draw() {
      if (this.drawing === 1) {
        this.drawing = 2
        this.newBox.x1 = this.clientX
        this.newBox.y1 = this.clientY
      } else if (this.drawing === 2) {
        this.drawing = 0
        this.dirty = true
        let x1 = Math.min(this.clientX, this.newBox.x1)
        let y1 = Math.min(this.clientY, this.newBox.y1)
        let x2 = Math.max(this.clientX, this.newBox.x1)
        let y2 = Math.max(this.clientY, this.newBox.y1)

        x1 = (x1 - this.imgLeft) / (this.imgHeight * this.ratio)
        y1 = (y1 - this.imgTop) / this.imgHeight
        x2 = (x2 - this.imgLeft) / (this.imgHeight * this.ratio)
        y2 = (y2 - this.imgTop) / this.imgHeight

        x1 = Math.max(0, Math.min(1, x1))
        y1 = Math.max(0, Math.min(1, y1))
        x2 = Math.max(0, Math.min(1, x2))
        y2 = Math.max(0, Math.min(1, y2))

        if ((x2 - x1) * (y2 - y1) > 0.00001) {
          const box = {
            label: this.task.labels[this.label],
            // x, y, w, h
            bbox: [x1, y1, x2 - x1, y2 - y1],
          }
          this.boxes.push(box)
        }
        this.label = -1
      }
    },
    goToEntity(idx) {
      let promise = null
      if (this.dirty) {
        promise = this.$store.dispatch('entity/labelEntity', {
          id: this.entity.id,
          data: {
            boxes: this.boxes,
          },
        })
      } else {
        promise = Promise.resolve()
      }
      return promise
        .then(() => {
          const entity = this.task.entities[idx]
          return this.$store.dispatch('entity/fetchEntity', entity.id)
        })
        .then(() => {
          this.index = idx
          this.showLabels = false
          this.drawing = 0
          this.boxes = this.entity.annotation
          this.chosenBox = null
          this.dirty = false
        })
    },
    saveThisEntity() {
      if (this.dirty) {
        this.$store.dispatch('entity/labelEntity', {
          id: this.entity.id,
          data: {
            annotation: this.boxes,
          },
        })
      }
    },
  },
  async mounted() {
    await new Promise((r) => setTimeout(r, 100)) // wait 100 ms
    window.onresize = this.adjustImage
  },
  beforeRouteEnter(to, from, next) {
    fetchTaskAndCheckIdentity(to.params.id, to, next)
  },
  beforeRouteUpdate(to, from, next) {
    fetchTaskAndCheckIdentity(to.params.id, to, next)
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
}
.hl {
  position: absolute;
  border-top-width: 1px;
  border-top-color: red;
  width: 100%;
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
