<template>
  <v-container mt-5>
    <p class="display-1">新建任务</p>
    <v-form>
      <v-row>
        <v-col cols="6">
          <v-text-field label="任务名" v-model="newTask.name" required>
          </v-text-field>
        </v-col>
        <v-col cols="6">
          <v-select
            label="任务类型"
            v-model="newTask.type"
            :items="taskTypes"
            required
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
        <v-btn @click.prevent="submit">创建任务</v-btn>
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
    }
  },
  computed: {},
  methods: {
    submit() {
      this.$store.dispatch('task/createTask', this.newTask).then(() => {
        const id = this.$store.state.task.task.id
        this.$store.dispatch('message/pushSuccess', '任务创建成功。')
        this.$router.push({ name: 'task', params: { id: id } })
      })
    },
  },
}
</script>
