<template>
  <v-sheet id="canvas" ref="canvas" height="100vh" class="grey darken-2">
    <img
      ref="image"
      id="image"
      alt="image"
      :src="image"
      :style="imageStyle"
      @mousemove.prevent
      @load="adjustImage"
    />

    <template v-if="!bboxes">
      <v-card
        class="labels-display transparent elevation-0"
        :style="labelsDispalyStyle"
      >
        <v-card-text class="text-center">
          <v-chip
            v-for="(label, index) in labels"
            :key="index"
            class="text-h6 mx-1"
            color="rgb(192,192,192,0.75)"
          >
            {{ label }}
          </v-chip>
        </v-card-text>
      </v-card>
    </template>

    <template v-if="bboxes">
      <label-panel-box
        v-for="index in bboxes.length"
        :key="index"
        :height="imgHeight"
        :width="imgHeight * imgRatio"
        :left="imgLeft"
        :top="imgTop"
        :box="bboxes[index - 1]"
        :label="labels[index - 1]"
        :selected="false"
        :review-mode="true"
      ></label-panel-box>
    </template>
    <slot></slot>
  </v-sheet>
</template>

<script>
import LabelPanelBox from '@/components/LabelPanelBox'

export default {
  components: { LabelPanelBox },

  props: {
    image: {
      type: String,
      required: true,
    },
    bboxes: {
      type: Array,
      required: false,
    },
    labels: {
      type: Array,
      required: true,
    },
    viewOnly: {
      type: Boolean,
      default: false,
    },
  },

  data: () => ({
    imgHeight: 100, // image height
    imgRatio: 1,
    imgLeft: 0, // image "left" css property
    imgTop: 0, // image "top" css property
  }),

  computed: {
    imageStyle() {
      return {
        position: 'absolute',
        height: this.imgHeight + 'px',
        left: this.imgLeft + 'px',
        top: this.imgTop + 'px',
      }
    },

    labelsDispalyStyle() {
      return {
        bottom: (this.viewOnly ? 35 : 95) + 'px',
      }
    },
  },

  methods: {
    adjustImage() {
      let canvasWidth = document.getElementById('canvas').offsetWidth
      let canvasHeight = document.getElementById('canvas').offsetHeight - 40
      console.log('canvas:', canvasWidth, canvasHeight)
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
  },

  mounted() {
    window.onresize = this.adjustImage
  },
}
</script>

<style scoped>
.labels-display {
  position: absolute;

  width: 100%;
}
</style>
