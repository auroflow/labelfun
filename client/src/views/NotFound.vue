<template>
  <v-container mt-5>
    <p class="display-1">找不到页面。</p>
    <v-btn class="primary mt-5" :to="{ name: 'home' }">返回首页</v-btn>
  </v-container>
</template>

<script>
export default {
  name: 'NotFound',
}
</script>

<style scoped></style>
