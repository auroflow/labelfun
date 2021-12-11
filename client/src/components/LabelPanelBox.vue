<template>
  <div class="box" :style="boxStyle"></div>
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
  },
  data() {
    return {
      x: this.box.bbox[0],
      y: this.box.bbox[1],
      w: this.box.bbox[2],
      h: this.box.bbox[3],
    }
  },
  computed: {
    boxStyle() {
      return {
        borderStyle: this.box === this.chosenBox ? 'solid' : 'solid',
        left: this.left + this.x * this.width + 'px',
        width: this.w * this.width + 'px',
        top: this.top + this.y * this.height + 'px',
        height: this.h * this.height + 'px',
      }
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
</style>
