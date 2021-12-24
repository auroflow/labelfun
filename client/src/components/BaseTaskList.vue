<template>
  <v-data-iterator :items="tasks" item-key="id" hide-default-footer>
    <template slot="no-data">
      <v-container> 无任务。 </v-container>
    </template>
    <template v-slot:default="{ items }">
      <v-container>
        <v-row>
          <v-col
            v-for="task in items"
            :key="task.id"
            cols="12"
            md="6"
            lg="4"
            xl="3"
          >
            <v-card elevation="2" rounded>
              <v-card-title>{{ task.name }}</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="3">
                    <p>任务类型</p>
                    <p>任务状态</p>
                    <p>创建人</p>
                    <p>创建时间</p>
                    <p>标签</p>
                  </v-col>
                  <v-col>
                    <p>{{ taskTypes[task.type] }}</p>
                    <p>{{ taskProgresses[task.progress] }}</p>
                    <p>{{ task.creator.name }}</p>
                    <p>{{ formatDate(task.time) }}</p>
                    <p>
                      <v-chip
                        v-for="label in task.labels.slice(0, 5)"
                        :key="label"
                        class="mr-1 mt-1"
                        small
                      >
                        {{ label }}
                      </v-chip>
                      <v-chip v-if="task.labels.length > 5" small>...</v-chip>
                    </p>
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions>
                <v-btn
                  :to="{ name: 'task', params: { id: task.id } }"
                  class="primary"
                >
                  查看详情
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </template>
  </v-data-iterator>
</template>

<script>
export default {
  props: {
    tasks: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      tab: null,
      taskTypes: {
        image_cls: '图像分类',
        image_seg: '图像物体探测',
        video_seg: '视频物体探测',
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
  methods: {
    formatDate(str) {
      return new Date(str).toLocaleDateString('zh-CN')
    },
  },
}
</script>
