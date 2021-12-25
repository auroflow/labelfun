<template>
  <v-container mt-5>
    <p class="text-h4">{{ task.name }} - 任务详情</p>
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

    <!-- Buttons -->
    <template
      v-if="task.progress === 'unpublished' && task.creator.id === user.id"
    >
      <v-btn class="mr-2 primary" @click="showAddEntities">
        添加{{ ENTITY }}
      </v-btn>
      <v-btn class="mr-2 primary" @click="showModify">修改任务</v-btn>
      <v-btn class="mr-2 secondary" dark @click="publish">发布任务</v-btn>
      <v-btn class="mr-2 error" @click="deleteTask">删除任务</v-btn>
    </template>

    <template v-if="task.progress === 'unlabeled'">
      <v-btn class="mr-2 primary" @click="claimTask('label')">
        领取标注任务
      </v-btn>
    </template>

    <template v-if="task.progress === 'labeling'">
      <v-btn
        class="mr-2 primary"
        v-if="task.labeler.id === user.id"
        :to="{
          name: label[task.type],
          params: { task_id: task.id, entity_idx: 0 },
        }"
      >
        去标注
      </v-btn>
      <v-btn
        class="mr-2 secondary"
        v-if="task.label_done"
        @click="completeTask('label')"
      >
        提交标注结果
      </v-btn>
    </template>

    <template v-if="task.progress === 'unreviewed'">
      <v-btn class="mr-2 primary" @click="claimTask('review')">
        领取审核任务
      </v-btn>
    </template>

    <template v-if="task.progress === 'reviewing'">
      <v-btn
        class="mr-2 primary"
        v-if="task.reviewer.id === user.id"
        :to="{
          name: 'review',
          params: { task_id: task.id, entity_idx: 0 },
        }"
      >
        去审核
      </v-btn>
      <v-btn
        class="mr-2 secondary"
        v-if="task.review_done"
        @click="completeTask('review')"
      >
        提交审核结果
      </v-btn>
    </template>

    <template v-if="task.progress === 'done'">
      <v-btn
        class="mr-2 primary"
        :to="{
          name: 'view',
          params: { task_id: task.id, entity_idx: 0 },
        }"
      >
        查看标注
      </v-btn>
      <v-btn class="mr-2 secondary" @click="exporting = true"> 导出标注 </v-btn>
    </template>

    <!-- Entities preview -->
    <p class="text-h5 mt-5">{{ ENTITY }}概览</p>
    <v-row class="mb-5" justify="start" dense>
      <v-col
        v-for="entity in task.entities"
        :key="entity.id"
        class="col-3 col-ms-2 col-lg-1"
      >
        <v-hover>
          <template v-slot:default="{ hover }">
            <v-img
              :src="
                baseURL +
                entity.thumb_key +
                (task.type === 'video_seg' ? '-000001' : '')
              "
              lazy-src="/loading.jpg"
            >
              <v-fade-transition>
                <v-overlay
                  v-if="task.published ? false : hover"
                  absolute
                  color="#036358"
                >
                  <v-icon color="warning" @click="deleteEntity(entity.id)"
                    >mdi-close-circle</v-icon
                  >
                </v-overlay>
              </v-fade-transition>
            </v-img>
          </template>
        </v-hover>
      </v-col>
    </v-row>

    <!-- Upload entities -->
    <v-dialog
      v-model="showDialog"
      persistent
      max-width="600px"
      class="rounded-lg"
    >
      <v-card rounded class="rounded-lg">
        <v-card-title>添加{{ ENTITY }}</v-card-title>
        <v-card-text>
          <v-file-input
            :label="'选择' + ENTITY"
            :accept="ACCEPT"
            v-model="files"
            multiple
            small-chips
            required
          ></v-file-input>
          <p v-if="task.type === 'video_seg'">
            视频上传后，将每隔 {{ task.interval }} 秒提取一帧。
          </p>
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

    <!-- Edit task -->
    <v-dialog v-model="modifying" persistent max-width="400px">
      <v-form ref="modifyForm">
        <v-card>
          <v-card-title>修改任务信息</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="newName"
              label="任务名"
              :rules="taskNameRules"
              required
            >
            </v-text-field>
            <v-combobox
              label="可供标注的标签"
              v-model="newLabels"
              multiple
              :append-icon="null"
              required
              chips
              :rules="labelRules"
              deletable-chips
            >
              <template v-slot:no-data>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title
                      >按 <kbd>回车</kbd> 添加新标签</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-combobox>
          </v-card-text>
          <v-card-actions>
            <v-btn @click="modifying = false">取消</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="modifyTask">保存</v-btn>
          </v-card-actions>
        </v-card>
      </v-form>
    </v-dialog>

    <!-- Export -->
    <v-dialog v-model="exporting" persistent max-width="400px">
      <v-form ref="exportForm">
        <v-card>
          <v-card-title>导出任务</v-card-title>
          <v-card-text>
            <v-select
              label="导出类型"
              v-model="exportOptions.export_type"
              :items="allowed_export_types[task.type]"
              required
            ></v-select>
          </v-card-text>
          <v-card-actions>
            <v-btn @click="exporting = false">取消</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="exportTask">保存</v-btn>
          </v-card-actions>
        </v-card>
      </v-form>
    </v-dialog>

    <v-dialog v-model="exportInProgress" persistent max-width="300px">
      <v-card>
        <v-card-title>正在导出……</v-card-title>
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
import NProgress from 'nprogress'
import APIService from '@/services/APIService'

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
        image_seg: '图像物体探测',
        video_seg: '视频物体探测',
      },
      label: {
        image_cls: 'label-cls',
        image_seg: 'label-img',
        video_seg: 'label-vid',
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
      modifying: false,
      newName: null,
      newLabels: [],
      taskNameRules: [
        (v) => !!v || '请输入任务名。',
        (v) => v.length < 120 || '任务名过长。',
      ],
      labelRules: [
        (v) => !!v.length || '请填写标签。',
        (v) => v.every((item) => !!item.length) || '标签文字不能为空。',
      ],
      exporting: false,
      exportInProgress: false,
      allowed_export_types: {
        image_cls: [
          {
            text: 'FiftyOne Image Classification Dataset',
            value: 'fiftyone',
          },
        ],
        image_seg: [
          {
            text: 'CVAT Image Dataset',
            value: 'cvat',
          },
          {
            text: 'COCO Detection Dataset',
            value: 'coco',
          },
          {
            text: 'VOC Detection Dataset',
            value: 'voc',
          },
          {
            text: 'KITTI Detection Dataset',
            value: 'kitti',
          },
        ],
        video_seg: [
          {
            text: 'CVAT Video Dataset',
            value: 'cvat',
          },
        ],
      },
      exportOptions: {
        export_type: null,
      },
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
      if (window.confirm(`确定领取此任务吗？`)) {
        this.$store
          .dispatch('task/claim', {
            id: this.task.id,
            action: action,
          })
          .then(() => {
            this.$store.dispatch('message/pushSuccess', '任务领取成功。')
          })
      }
    },
    completeTask(action) {
      const message =
        action === 'label'
          ? `确定提交标注结果吗？提交后，任务将会开放审核。`
          : `确定提交审核结果吗？`
      if (window.confirm(message)) {
        this.$store
          .dispatch('task/complete', {
            id: this.task.id,
            action: action,
          })
          .then(() => {
            let success = null
            if (this.task.status === 'unlabeled')
              success = '提交成功，等待标注者修改。'
            else if (this.task.status === 'unreviewed')
              success = '提交成功，请等待审核结果。'
            else success = '提交成功！该任务已完成。'
            this.$store.dispatch('message/pushSuccess', success)
          })
      }
    },
    upload() {
      if (!this.files.length) {
        this.$store.dispatch('message/push', {
          text: '请选择文件。',
          type: 'error',
        })
        return
      }
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
          this.$store.dispatch('message/pushSuccess', '上传完成。')
          this.files = []
        })
    },
    publish() {
      if (
        window.confirm(`确定发布此任务吗？发布之后不能撤销，也不能删除此任务。`)
      ) {
        this.$store.dispatch('task/publish', this.task.id).then(() => {
          this.$store.dispatch('message/pushSuccess', '任务发布成功。')
        })
      }
    },
    ...mapMutations('task', {
      showAddEntities: 'SHOW_ADD_ENTITIES',
      hideAddEntities: 'HIDE_ADD_ENTITIES',
    }),
    deleteTask() {
      if (
        window.confirm(
          `确定删除此任务吗？此任务下的所有${this.ENTITY}也将删除。`
        )
      ) {
        this.$store.dispatch('task/deleteTask', this.task.id).then(() => {
          this.$store.dispatch('message/pushSuccess', '任务已删除。')
          this.$router.push({ name: 'home' })
        })
      }
    },
    deleteEntity(id) {
      if (window.confirm(`确定删除此${this.ENTITY}吗？`)) {
        this.$store.dispatch('task/deleteEntity', id).then(() => {
          this.$store.dispatch('message/pushSuccess', `${this.ENTITY}已删除。`)
        })
      }
    },
    showModify() {
      this.newLabels = [...this.task.labels]
      this.newName = this.task.name
      this.modifying = true
    },
    modifyTask() {
      if (this.$refs.modifyForm.validate()) {
        NProgress.start()
        const data = {
          labels: this.newLabels,
          name: this.newName,
        }
        this.$store
          .dispatch('task/updateTask', {
            id: this.task.id,
            task: data,
          })
          .then(() => {
            this.$store.dispatch('message/pushSuccess', '任务修改成功。')
            this.modifying = false
          })
          .finally(() => {
            NProgress.done()
          })
      }
    },
    exportTask() {
      if (this.$refs.exportForm.validate()) {
        this.exportInProgress = true
        APIService.exportTask(this.task.id, this.exportOptions)
          .then(({ data }) => {
            const url = window.URL.createObjectURL(
              new Blob([data], { type: 'application/zip' })
            )
            const link = document.createElement('a')
            link.setAttribute(
              'download',
              this.task.id + '_' + this.exportOptions.export_type + '.zip'
            )
            link.href = url
            document.body.appendChild(link)
            link.click()
          })
          .catch((err) => {
            this.$store.dispatch('message/pushError', err)
          })
          .finally(() => {
            this.exportInProgress = false
            this.exporting = false
            this.$store.dispatch('message/pushSuccess', '导出成功。')
          })
      }
    },
  },
}
</script>
