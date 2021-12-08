<template>
  <v-container mt-5>
    <p class="display-1">任务详情</p>
    <p>类型：{{ taskTypes[task.type] }}</p>
    <p>发布者：{{ task.creator.name }}</p>
    <p v-if="task.labeler">标注者：{{ task.labeler.name }}</p>
    <p v-if="task.reviewer">审核者：{{ task.reviewer.name }}</p>
    <p>任务状态：{{ taskProgresses[task.progress] }}</p>
    <p v-if="task.progress !== 'unpublished' && task.progress !== 'done'">
      任务进度：共 {{ task.entity_count }} 项，已标注
      {{ task.labeled_count }} 项，已审核 {{ task.reviewed_count }} 项
    </p>
    <p>
      标签：
      <v-chip v-for="label in task.labels" :key="label" class="mr-1">
        {{ label }}
      </v-chip>
    </p>

    <template
      v-if="task.progress === 'unpublished' && task.creator.id === user.id"
    >
      <v-btn>
        添加<span v-if="task.type !== 'video_seg'">图片</span
        ><span v-else>视频</span>
      </v-btn>
      <v-btn>发布任务</v-btn>
    </template>

    <template v-if="task.progress === 'unlabeled'">
      <v-btn @click="claimTask('label')"> 领取标注任务 </v-btn>
    </template>

    <template v-if="task.progress === 'labeling'">
      <v-btn v-if="task.labeler.id === user.id"> 去标注 </v-btn>
    </template>

    <template v-if="task.progress === 'unreviewed'">
      <v-btn @click="claimTask('review')"> 领取审核任务 </v-btn>
    </template>

    <template v-if="task.progress === 'reviewing'">
      <v-btn v-if="task.reviewer.id === user.id"> 去审核 </v-btn>
    </template>

    <template v-if="task.progress === 'done'">
      <v-btn> 导出标注结果 </v-btn>
    </template>
  </v-container>
</template>

<script>
import store from '@/store'
import { mapState } from 'vuex'

function fetchTask(id, next) {
  store.dispatch('task/fetchTask', id).then(() => {
    next()
  })
}

export default {
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      tab: null,
      taskTypes: {
        image_cls: '图像分类',
        image_seg: '图像分割',
        video_seg: '视频分割',
      },
      taskProgresses: {
        unpublished: '尚未发布',
        unlabeled: '未标注',
        labeling: '正在标注',
        unreviewed: '未审核',
        reviewing: '正在审核',
        done: '已完成',
      },
    }
  },
  computed: {
    ...mapState({
      task: (state) => state.task.task,
      user: (state) => state.user.user,
    }),
  },
  beforeRouteEnter(to, from, next) {
    fetchTask(to.params.id, next)
  },
  beforeRouteUpdate(to, from, next) {
    fetchTask(to.params.id, next)
  },
  methods: {
    claimTask(action) {
      this.$store.dispatch('task/claim', {
        id: this.task.id,
        action: action,
      })
      this.$store.dispatch('message/pushSuccess', '任务领取成功。')
    },
    completeTask(action) {
      this.$store.dispatch('task/complete', {
        id: this.task.id,
        action: action,
      })
    },
  },
}
</script>
