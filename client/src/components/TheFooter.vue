<template>
  <v-footer color="transparent" padless>
    <v-col class="text-center" cols="12">
      {{ new Date().getFullYear() }} — <strong>{{ name }}</strong>
    </v-col>
  </v-footer>
</template>

<script>
export default {
  props: {
    name: {
      type: String,
      required: true,
    },
  },
}
</script>

<style scoped></style>
