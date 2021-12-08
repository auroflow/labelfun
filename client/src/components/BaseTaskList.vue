<template>
  <v-data-iterator :items="tasks" item-key="id" hide-default-footer>
    <template slot="no-data">
      <v-container> 无任务。 </v-container>
    </template>
    <template v-slot:default="{ items }">
      <v-container>
        <v-row>
          <v-col v-for="task in items" :key="task.id" cols="6">
            <v-card>
              <v-card-title>{{ task.name }}</v-card-title>
              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="4">任务类型</v-col>
                    <v-col>
                      {{ taskTypes[task.type] }}
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="4">任务状态</v-col>
                    <v-col>
                      {{ taskProgresses[task.progress] }}
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="4">创建人</v-col>
                    <v-col>
                      {{ task.creator.name }}
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="4">创建时间</v-col>
                    <v-col>
                      {{ formatDate(task.time) }}
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="4">标签</v-col>
                    <v-col>
                      <v-chip
                        v-for="label in task.labels.slice(0, 5)"
                        :key="label"
                        class="mr-1"
                        small
                      >
                        {{ label }}
                      </v-chip>
                      <v-chip v-if="task.labels.length > 5" small>...</v-chip>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>
              <v-card-actions>
                <v-btn :to="{ name: 'task', params: { id: task.id } }">
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
  methods: {
    formatDate(str) {
      return new Date(str).toLocaleDateString('zh-CN')
    },
  },
}
</script>
