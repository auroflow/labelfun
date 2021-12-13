<template>
  <div class="box label-selector" :style="boxStyle" @click="$emit('click')">
    <div
      class="box-corner upper-left"
      v-show="selected"
      @mousedown="startResize($event, 'upper-left')"
      :style="[upperLeftStyle]"
    ></div>
    <div
      class="box-corner upper-right"
      v-show="selected"
      @mousedown="startResize($event, 'upper-right')"
      :style="[upperRightStyle]"
    ></div>
    <div
      class="box-corner bottom-left"
      v-show="selected"
      @mousedown="startResize($event, 'bottom-left')"
      :style="[bottomLeftStyle]"
    ></div>
    <div
      class="box-corner bottom-right"
      v-show="selected"
      @mousedown="startResize($event, 'bottom-right')"
      :style="[bottomRightStyle]"
    ></div>
    <p class="box-caption" v-show="selected" :style="{ top: boxStyle.height }">
      x: {{ Number(box.bbox[0]).toFixed(3) }} y:
      {{ Number(box.bbox[1]).toFixed(3) }} w:
      {{ Number(box.bbox[2]).toFixed(3) }} h:
      {{ Number(box.bbox[3]).toFixed(3) }}
    </p>
  </div>
</template>

<script>
export default {
  props: {
    box: {
      type: Object,
      required: true,
    },
    top: {
      type: Number,
      required: true,
    },
    left: {
      type: Number,
      required: true,
    },
    width: {
      type: Number,
      required: true,
    },
    height: {
      type: Number,
      required: true,
    },
    selected: {
      type: Boolean,
      required: true,
    },
  },

  data: () => ({
    resizing: '',
  }),

  computed: {
    boxStyle() {
      const x = this.box.bbox[0]
      const y = this.box.bbox[1]
      const w = this.box.bbox[2]
      const h = this.box.bbox[3]
      return {
        borderStyle: this.selected ? 'solid' : 'dashed',
        backgroundColor: this.selected
          ? 'rgba(129,199,132,0.25)'
          : 'transparent',
        left: this.left + x * this.width + 'px',
        width: w * this.width + 'px',
        top: this.top + y * this.height + 'px',
        height: h * this.height + 'px',
        zIndex: 100 - Math.floor(w * h * 100),
      }
    },
    upperLeftStyle() {
      return {
        cursor: this.selected ? 'nw-resize' : 'default',
      }
    },
    upperRightStyle() {
      return {
        cursor: this.selected ? 'ne-resize' : 'default',
      }
    },
    bottomLeftStyle() {
      return {
        cursor: this.selected ? 'sw-resize' : 'default',
      }
    },
    bottomRightStyle() {
      return {
        cursor: this.selected ? 'se-resize' : 'default',
      }
    },
  },

  methods: {
    startResize(e, option) {
      this.$emit('start-resizing', option)
    },
  },
}
</script>

<style scoped>
.box {
  position: absolute;
  border-color: yellowgreen;
  border-width: 2px;
}
.box-corner {
  z-index: 101;
  position: absolute;
  background-color: yellowgreen;
  width: 11px;
  height: 11px;
}
.upper-left {
  left: -6px;
  top: -6px;
}
.upper-right {
  right: -6px;
  top: -6px;
}
.bottom-left {
  left: -6px;
  bottom: -6px;
}
.bottom-right {
  right: -6px;
  bottom: -6px;
}
.box-caption {
  position: absolute;
  left: 0px;
  background-color: yellowgreen;
  color: white;
  font-size: 12px;
  padding: 0 2px;
}
</style>
