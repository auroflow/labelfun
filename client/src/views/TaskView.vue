<template>
  <v-container mt-5>
    <p class="text-h4">任务详情</p>
    <p>类型：{{ taskTypes[task.type] }}</p>
    <p>发布者：{{ task.creator.name }}</p>
    <p v-if="task.labeler">标注者：{{ task.labeler.name }}</p>
    <p v-if="task.reviewer">审核者：{{ task.reviewer.name }}</p>
    <p>任务状态：{{ taskProgresses[task.progress] }}</p>
    <p v-if="task.progress !== 'done'">
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
      <v-btn class="mr-2" @click="showAddEntities"> 添加{{ ENTITY }} </v-btn>
      <v-btn class="mr-2" @click="publish">发布任务</v-btn>
    </template>

    <template v-if="task.progress === 'unlabeled'">
      <v-btn class="mr-2" @click="claimTask('label')"> 领取标注任务 </v-btn>
    </template>

    <template v-if="task.progress === 'labeling'">
      <v-btn
        class="mr-2"
        v-if="task.labeler.id === user.id"
        :to="{ name: 'label', params: { task_id: task.id, entity_idx: 0 } }"
      >
        去标注
      </v-btn>
    </template>

    <template v-if="task.progress === 'unreviewed'">
      <v-btn class="mr-2" @click="claimTask('review')"> 领取审核任务 </v-btn>
    </template>

    <template v-if="task.progress === 'reviewing'">
      <v-btn class="mr-2" v-if="task.reviewer.id === user.id"> 去审核 </v-btn>
    </template>

    <template v-if="task.progress === 'done'">
      <v-btn class="mr-2"> 导出标注结果 </v-btn>
    </template>

    <p class="text-h5 mt-5">{{ ENTITY }}概览</p>

    <v-row class="mb-5" justify="start" dense>
      <v-col
        v-for="entity in task.entities"
        :key="entity.id"
        class="col-3 col-ms-2 col-lg-1"
      >
        <v-img :src="baseURL + entity.thumb_key"></v-img>
      </v-col>
    </v-row>

    <v-dialog v-model="showDialog" persistent max-width="600px">
      <v-card>
        <v-card-title>添加{{ ENTITY }}</v-card-title>
        <v-card-text>
          <v-file-input
            :label="'选择' + ENTITY"
            :accept="ACCEPT"
            v-model="files"
            multiple
            small-chips
          ></v-file-input>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="hideAddEntities">取消</v-btn>
          <v-spacer></v-spacer>
          <v-btn @click="upload" color="primary">上传</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="uploading" persistent max-width="400px">
      <v-card>
        <v-card-title>正在上传……</v-card-title>
        <v-progress-linear
          color="primary"
          indeterminate
          height="6"
        ></v-progress-linear>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import store from '@/store'
import { mapMutations, mapState } from 'vuex'

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
      files: [],
    }
  },
  computed: {
    ...mapState({
      baseURL: (state) => state.baseURL,
      task: (state) => state.task.task,
      user: (state) => state.user.user,
      uploading: (state) => state.task.uploading,
      showDialog: (state) => state.task.showDialog,
    }),
    ENTITY() {
      return this.task.type !== 'video_seg' ? '图片' : '视频'
    },
    ACCEPT() {
      return this.task.type !== 'video_seg' ? 'image/*' : 'video/*'
    },
  },
  beforeRouteEnter(to, from, next) {
    fetchTask(to.params.id, next)
  },
  beforeRouteUpdate(to, from, next) {
    fetchTask(to.params.id, next)
  },
  methods: {
    claimTask(action) {
      this.$store
        .dispatch('task/claim', {
          id: this.task.id,
          action: action,
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '任务领取成功。')
        })
    },
    completeTask(action) {
      this.$store
        .dispatch('task/complete', {
          id: this.task.id,
          action: action,
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '任务完成成功。')
        })
    },
    upload() {
      const data = {
        task_id: this.task.id,
        paths: [],
      }
      for (let file of this.files) {
        data.paths.push(file.name)
      }
      this.$store
        .dispatch('task/addEntities', {
          request_data: data,
          files: this.files,
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '上传成功。')
          this.files = []
        })
        .catch((err) => this.$store.dispatch('message/pushError', err))
    },
    publish() {
      this.$store.dispatch('task/publish', this.task.id).then(() => {
        this.$store.dispatch('message/pushSuccess', '任务发布成功。')
      })
    },
    ...mapMutations('task', {
      showAddEntities: 'SHOW_ADD_ENTITIES',
      hideAddEntities: 'HIDE_ADD_ENTITIES',
    }),
  },
}
</script>
