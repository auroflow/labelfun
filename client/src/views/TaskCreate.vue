<template>
  <v-container mt-5>
    <p class="display-1">新建任务</p>
    <v-form ref="newTaskForm">
      <v-row>
        <v-col cols="6">
          <v-text-field
            label="任务名"
            v-model="newTask.name"
            :rules="taskNameRules"
            required
          >
          </v-text-field>
        </v-col>
        <v-col cols="6">
          <v-select
            label="任务类型"
            v-model="newTask.type"
            :items="taskTypes"
            required
            :rules="taskTypeRules"
          ></v-select>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-combobox
            label="可供标注的标签"
            v-model="newTask.labels"
            multiple
            :append-icon="null"
            required
            :rules="labelRules"
            chips
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
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-slider
            label="视频每帧间隔（秒）"
            v-model="newTask.interval"
            v-if="newTask.type === 'video_seg'"
            min="0.1"
            step="0.1"
            max="5"
            thumb-label="always"
          ></v-slider>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-btn class="primary" @click.prevent="submit">创建任务</v-btn>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      newTask: {
        name: '',
        type: null,
        labels: [],
        interval: 0.5,
      },
      taskTypes: [
        {
          text: '图像分类',
          value: 'image_cls',
        },
        {
          text: '图像物体探测',
          value: 'image_seg',
        },
        {
          text: '视频物体探测',
          value: 'video_seg',
        },
      ],
      taskNameRules: [
        (v) => !!v || '请输入任务名。',
        (v) => v.length < 120 || '任务名过长。',
      ],
      taskTypeRules: [(v) => !!v || '请选择任务类型。'],
      labelRules: [
        (v) => !!v.length || '请填写标签。',
        (v) => v.every((item) => !!item.length) || '标签文字不能为空。',
      ],
    }
  },
  computed: {},
  methods: {
    submit() {
      if (this.$refs.newTaskForm.validate()) {
        this.createTask()
      }
    },
    createTask() {
      this.$store.dispatch('task/createTask', this.newTask).then(() => {
        const id = this.$store.state.task.task.id
        this.$store.dispatch('message/pushSuccess', '任务创建成功。')
        this.$router.push({ name: 'task', params: { id: id } })
      })
    },
  },
}
</script>
