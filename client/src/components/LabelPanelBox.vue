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

  computed: {
    boxStyle() {
      const x = this.box.bbox[0]
      const y = this.box.bbox[1]
      const w = this.box.bbox[2]
      const h = this.box.bbox[3]
      return {
        borderStyle: this.box === this.chosenBox ? 'solid' : 'solid',
        left: this.left + x * this.width + 'px',
        width: w * this.width + 'px',
        top: this.top + y * this.height + 'px',
        height: h * this.height + 'px',
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
