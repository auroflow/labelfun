<template>
  <v-sheet
    id="canvas"
    ref="canvas"
    height="100vh"
    class="grey darken-2"
    @start-drawing="startDrawing"
    @mousedown="draw"
    @mousemove.prevent="
      drag($event)
      updateCursor($event)
    "
    @mouseup="resizing = ''"
    @wheel="resizeImage"
  >
    <img
      ref="image"
      id="image"
      alt="image"
      draggable="true"
      :src="url ? url : baseURL + image.key"
      :style="imgStyle"
      @load="adjustImage"
    />

    <div class="vl" :style="vlStyle"></div>
    <div class="hl" :style="hlStyle"></div>
    <div class="new-box" :style="newBoxStyle"></div>
    <label-panel-box
      v-for="(box, index) in boxes"
      :key="index"
      :height="imgHeight"
      :width="imgHeight * imgRatio"
      :left="imgLeft"
      :top="imgTop"
      :box="box"
      :selected="box === chosenBox"
      @click="chooseBox(box)"
      @start-resizing="resizing = $event"
      @end-resizing="resizing = ''"
    ></label-panel-box>

    <p
      style="position: absolute; right: 0px"
      class="white--text grey darken-2 px-2"
      v-show="canvasDrawing"
    >
      ({{ Number(relativeX).toFixed(3) }}, {{ Number(relativeY).toFixed(3) }})
    </p>
  </v-sheet>
</template>

<script>
import LabelPanelBox from '@/components/LabelPanelBox'
import { mapState } from 'vuex'

export default {
  components: {
    LabelPanelBox,
  },
  props: {
    image: {
      type: Object,
      required: true,
    },
    boxes: {
      type: Array,
      required: true,
    },
    inLabelChooser: {
      type: Boolean,
      required: true,
    },
    canvasDrawing: {
      type: Boolean,
      required: true,
    },
    chosenBox: {
      type: Object,
      required: true,
    },
    url: {
      type: String,
    },
  },

  watch: {
    canvasDrawing() {
      if (this.canvasDrawing) this.startDrawing()
    },
  },

  data: () => ({
    drawing: 0,
    resizing: false,
    cursorX: 0,
    cursorY: 0,
    initialCursorX: 0,
    initialCursorY: 0,
    newBox: {
      x1: null,
      y1: null,
    },
    imgHeight: null, // image height
    imgRatio: null,
    imgLeft: null, // image "left" css property
    imgTop: null, // image "top" css property
  }),

  computed: {
    ...mapState(['baseURL']),
    relativeX() {
      return (this.cursorX - this.imgLeft) / (this.imgHeight * this.imgRatio)
    },
    relativeY() {
      return (this.cursorY - this.imgTop) / this.imgHeight
    },
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
        left: this.cursorX + 'px',
      }
    },
    hlStyle() {
      return {
        borderTopStyle: this.drawing ? 'solid' : 'none',
        top: this.cursorY + 'px',
      }
    },
    newBoxStyle() {
      if (this.drawing === 2) {
        let x1 = this.imgLeft + this.imgHeight * this.imgRatio * this.newBox.x1
        let y1 = this.imgTop + this.imgHeight * this.newBox.y1
        let x2 = this.cursorX
        let y2 = this.cursorY

        return {
          borderStyle: 'solid',
          left: Math.min(x1, x2) + 'px',
          width: Math.abs(x1 - x2) + 'px',
          top: Math.min(y1, y2) + 'px',
          height: Math.abs(y1 - y2) + 'px',
        }
      } else {
        return {
          borderStyle: 'none',
        }
      }
    },
  },

  methods: {
    updateCursor(e) {
      this.cursorX = e.clientX - 50
      this.cursorY = e.clientY
    },

    adjustImage() {
      let canvasWidth = document.getElementById('canvas').offsetWidth
      let canvasHeight = document.getElementById('canvas').offsetHeight
      let canvasRatio = canvasWidth / canvasHeight
      this.imgRatio =
        this.$refs.image.naturalWidth / this.$refs.image.naturalHeight
      if (this.imgRatio < canvasRatio) {
        this.imgHeight = canvasHeight
      } else {
        this.imgHeight = (canvasHeight * canvasRatio) / this.imgRatio
      }
      this.imgLeft =
        this.imgRatio > canvasRatio
          ? 0
          : (canvasWidth - this.imgHeight * this.imgRatio) / 2
      this.imgTop =
        this.imgRatio > canvasRatio ? (canvasHeight - this.imgHeight) / 2 : 0
    },

    drag(e) {
      if (
        e.buttons === 1 &&
        !this.inLabelChooser &&
        !this.drawing &&
        !this.resizing
      ) {
        // drag image
        // calculate the new cursor position:
        const cursorDX = this.cursorX - this.initialCursorX
        const cursorDY = this.cursorY - this.initialCursorY
        // set the element's new position:
        this.imgLeft += cursorDX
        this.imgTop += cursorDY
      } else if (this.resizing) {
        // resizing chosen box

        const cursorDX =
          (this.cursorX - this.initialCursorX) /
          (this.imgHeight * this.imgRatio)
        const cursorDY = (this.cursorY - this.initialCursorY) / this.imgHeight

        if (this.resizing === 'upper-left') {
          const nx = this.chosenBox.bbox[0] + cursorDX
          const ny = this.chosenBox.bbox[1] + cursorDY
          const nw = this.chosenBox.bbox[2] - cursorDX
          const nh = this.chosenBox.bbox[3] - cursorDY
          console.log('resizing upper left:', nx, ny, nw, nh)
          if (nx >= 0 && ny >= 0 && nw >= 0 && nh >= 0) {
            this.$emit('resize-box', {
              index: this.boxes.indexOf(this.chosenBox),
              bbox: [nx, ny, nw, nh],
            })
          } else {
            this.resizing = ''
          }
        } else if (this.resizing === 'upper-right') {
          const nx = this.chosenBox.bbox[0]
          const ny = this.chosenBox.bbox[1] + cursorDY
          const nw = this.chosenBox.bbox[2] + cursorDX
          const nh = this.chosenBox.bbox[3] - cursorDY
          console.log('resizing upper left:', nx, ny, nw, nh)
          if (ny >= 0 && nh >= 0 && nw >= 0 && nx + nw <= 1) {
            this.$emit('resize-box', {
              index: this.boxes.indexOf(this.chosenBox),
              bbox: [nx, ny, nw, nh],
            })
          } else {
            this.resizing = ''
          }
        } else if (this.resizing === 'bottom-left') {
          const nx = this.chosenBox.bbox[0] + cursorDX
          const ny = this.chosenBox.bbox[1]
          const nw = this.chosenBox.bbox[2] - cursorDX
          const nh = this.chosenBox.bbox[3] + cursorDY
          console.log('resizing upper left:', nx, ny, nw, nh)
          if (nx >= 0 && nw >= 0 && nh >= 0 && ny + nh <= 1) {
            this.$emit('resize-box', {
              index: this.boxes.indexOf(this.chosenBox),
              bbox: [nx, ny, nw, nh],
            })
          } else {
            this.resizing = ''
          }
        } else if (this.resizing === 'bottom-right') {
          const nx = this.chosenBox.bbox[0]
          const ny = this.chosenBox.bbox[1]
          const nw = this.chosenBox.bbox[2] + cursorDX
          const nh = this.chosenBox.bbox[3] + cursorDY
          console.log('resizing upper left:', nx, ny, nw, nh)
          if (nh >= 0 && ny + nh <= 1 && nw >= 0 && nx + nw <= 1) {
            this.$emit('resize-box', {
              index: this.boxes.indexOf(this.chosenBox),
              bbox: [nx, ny, nw, nh],
            })
          } else {
            this.resizing = ''
          }
        }
      }
      this.initialCursorX = this.cursorX
      this.initialCursorY = this.cursorY
    },

    resizeImage(e) {
      if (!this.inLabelChooser) {
        const delta = e.deltaY * -0.0005
        this.imgHeight += this.imgHeight * delta
        this.imgLeft = (1 + delta) * this.imgLeft - delta * this.cursorX
        this.imgTop = (1 + delta) * this.imgTop - delta * this.cursorY
      }
    },

    startDrawing() {
      this.drawing = 1
      document.body.style.cursor = 'crosshair'
    },

    draw() {
      if (this.drawing === 1) {
        this.drawing = 2
        this.newBox.x1 = this.relativeX
        this.newBox.y1 = this.relativeY
      } else if (this.drawing === 2) {
        this.drawing = 0
        document.body.style.cursor = 'default'
        this.dirty = true

        let x1_ = this.newBox.x1
        let y1_ = this.newBox.y1
        let x2_ = this.relativeX
        let y2_ = this.relativeY

        let x1 = Math.max(0, Math.min(1, Math.min(x1_, x2_)))
        let y1 = Math.max(0, Math.min(1, Math.min(y1_, y2_)))
        let x2 = Math.max(0, Math.min(1, Math.max(x1_, x2_)))
        let y2 = Math.max(0, Math.min(1, Math.max(y1_, y2_)))

        if ((x2 - x1) * (y2 - y1) > 0.0001) {
          const bbox = [x1, y1, x2 - x1, y2 - y1]
          this.$emit('new-box-drawn', bbox)
        } else {
          this.$emit('new-box-drawn', null)
        }
      }
    },

    chooseBox(box) {
      this.$emit('choose-box', box)
    },
  },

  mounted() {
    window.onresize = this.adjustImage
  },
}
</script>

<style scoped>
#canvas {
  overflow: hidden;
  position: relative;
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
  border-color: yellow;
  border-width: 2px;
}
.box {
  position: absolute;
  border-color: yellowgreen;
  border-width: 2px;
}
</style>
