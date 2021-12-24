<template>
  <v-app class="grey darken-2">
    <the-message-bar></the-message-bar>
    <v-navigation-drawer
      :value="true"
      app
      stateless
      dark
      mini-variant
      mini-variant-width="50px"
      @mousemove.prevent
    >
      <!-- Go back -->
      <v-tooltip right color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            block
            icon
            width="50"
            height="50"
            v-bind="attrs"
            v-on="on"
            :to="{ name: 'task', params: { id: task_id.toString() } }"
          >
            <v-icon dark size="30"> mdi-arrow-left-circle </v-icon>
          </v-btn>
        </template>
        <span>返回</span>
      </v-tooltip>

      <!-- Add box -->
      <v-tooltip right color="grey darken-3">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            tile
            block
            icon
            max-width="10"
            height="50"
            v-bind="attrs"
            v-on="on"
            @click="toggleLabelChooser"
          >
            <v-icon dark size="30"> mdi-vector-square-plus </v-icon>
          </v-btn>
        </template>
        <span>添加选框</span>
      </v-tooltip>

      <template v-slot:append>
        <!-- First entity -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              v-bind="attrs"
              v-on="on"
              :disabled="entity_idx === 0"
              @click="goToEntity(0)"
            >
              <v-icon dark size="30"> mdi-chevron-double-up </v-icon>
            </v-btn>
          </template>
          <span>第一个</span>
        </v-tooltip>

        <!-- Previous entity -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              v-bind="attrs"
              v-on="on"
              :disabled="entity_idx === 0"
              @click="goToEntity(entity_idx - 1)"
            >
              <v-icon dark size="30"> mdi-chevron-up </v-icon>
            </v-btn>
          </template>
          <span>上一个</span>
        </v-tooltip>

        <!-- This count -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon dark size="30"> mdi-circle-small </v-icon>
            </v-btn>
          </template>
          <span>{{ entity_idx + 1 }} / {{ task.entities.length }}</span>
        </v-tooltip>

        <!-- Next entity -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              :disabled="entity_idx === task.entities.length - 1"
              v-bind="attrs"
              v-on="on"
              @click="goToEntity(entity_idx + 1)"
            >
              <v-icon dark size="30"> mdi-chevron-down </v-icon>
            </v-btn>
          </template>
          <span>下一个</span>
        </v-tooltip>

        <!-- Last entity -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              :disabled="entity_idx === task.entities.length - 1"
              v-bind="attrs"
              v-on="on"
              @click="goToEntity(task.entities.length - 1)"
            >
              <v-icon dark size="30"> mdi-chevron-double-down </v-icon>
            </v-btn>
          </template>
          <span>最后一个</span>
        </v-tooltip>

        <!-- Save -->
        <v-tooltip right color="grey darken-3">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              tile
              block
              icon
              max-width="10"
              height="50"
              v-bind="attrs"
              v-on="on"
              @click="saveChanges"
            >
              <v-icon dark size="30"> mdi-content-save </v-icon>
            </v-btn>
          </template>
          <span>保存</span>
        </v-tooltip>
      </template>
    </v-navigation-drawer>

    <v-navigation-drawer
      :value="true"
      app
      right
      width="300px"
      dark
      stateless
      @mousemove.prevent
    >
      <v-list-item>
        <v-list-item-title class="text-center">分类信息</v-list-item-title>
      </v-list-item>
      <transition-group name="v-expand-transition">
        <div
          v-for="(label, index) in entity.annotation"
          :key="index"
          class="mx-4"
        >
          <v-alert
            border="left"
            color="green"
            class="label-selector"
            dark
            dense
            transition="v-expand-transition"
          >
            <v-chip color="green lighten-2" class="mr-2">{{ label }}</v-chip>
            <template v-slot:append>
              <v-icon @click="deleteLabel(label)">mdi-close-circle</v-icon>
            </template>
          </v-alert>
        </div>
      </transition-group>
    </v-navigation-drawer>

    <v-main>
      <v-dialog-transition>
        <v-sheet
          style="z-index: 100"
          v-show="showLabels"
          elevation="10"
          rounded="xl"
          width="300"
          id="label-chooser"
          @mouseover="inLabelChooser = true"
          @mouseout="inLabelChooser = false"
        >
          <v-sheet class="pa-2 grey darken-3" dark rounded="t-xl">
            <v-container>
              <v-row>
                <p class="text-body-1 my-auto mx-2">选择标签</p>
                <v-spacer></v-spacer>
                <v-btn icon @click="closeAndClearLabelChooser">
                  <v-icon>mdi-close</v-icon>
                </v-btn>
                <v-btn
                  class="ml-2"
                  icon
                  @click="addLabel"
                  :disabled="label === -1"
                >
                  <v-icon>mdi-check</v-icon>
                </v-btn>
              </v-row>
            </v-container>
          </v-sheet>

          <v-sheet class="pa-4" rounded="b-xl">
            <v-chip-group active-class="grey" v-model="label" column>
              <v-chip
                v-for="tag in task.labels"
                class=""
                :key="tag"
                :disabled="entity.annotation.find((element) => element === tag)"
              >
                {{ tag }}
              </v-chip>
            </v-chip-group>
          </v-sheet>
        </v-sheet>
      </v-dialog-transition>
      <label-panel-canvas
        :in-label-chooser="inLabelChooser"
        :image="entity"
        :boxes="null"
        :canvas-drawing="false"
        :chosen-box="null"
      ></label-panel-canvas>
    </v-main>
  </v-app>
</template>

<script>
import store from '@/store'
import { mapState } from 'vuex'
import TheMessageBar from '@/components/TheMessageBar'
import LabelPanelCanvas from '@/components/LabelPanelCanvas'

function fetchTaskAndEntity(task_id, entity_idx, next) {
  store
    .dispatch('task/fetchTask', task_id)
    .then(() => {
      if (store.state.user.user.id !== store.state.task.task.labeler?.id) {
        return Promise.reject({ message: '无标注权限。' })
      } else {
        const entities = store.state.task.task.entities
        if (entity_idx < 0 || entity_idx >= entities.length) {
          return Promise.reject({ message: '任务无此图片或视频。' })
        } else {
          const entity_id = store.state.task.task.entities[entity_idx].id
          return store.dispatch('entity/fetchEntity', entity_id)
        }
      }
    })
    .then(() => {
      next()
    })
    .catch((err) => {
      store.dispatch('message/pushError', err)
    })
}

export default {
  components: {
    TheMessageBar,
    LabelPanelCanvas,
  },
  props: {
    task_id: {
      type: Number,
      required: true,
    },
    entity_idx: {
      type: Number,
      required: true,
    },
  },

  data: () => ({
    dirty: false,
    label: -1, // chosen label index
    showLabels: false, // whether the label chooser is shown
    inLabelChooser: false, // whether the cursor is in label chooser
  }),
  computed: {
    ...mapState({
      baseURL: (state) => state.baseURL,
      task: (state) => state.task.task,
      user: (state) => state.user.user,
      entity: (state) => state.entity.entity,
    }),
  },
  methods: {
    closeAndClearLabelChooser() {
      this.label = -1
      this.showLabels = false
    },

    toggleLabelChooser() {
      if (this.showLabels) {
        this.closeAndClearLabelChooser()
      } else {
        this.showLabels = true
      }
    },

    addLabel() {
      this.dirty = true
      this.$store.dispatch('entity/addLabel', this.task.labels[this.label])
      this.label = -1
      this.showLabels = false
    },

    deleteLabel(label) {
      this.dirty = true
      this.$store.dispatch('entity/deleteLabel', label)
    },

    saveChanges() {
      return this.$store
        .dispatch('entity/labelEntity', {
          id: this.entity.id,
          data: {
            labels: this.entity.annotation,
          },
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '已保存修改。')
        })
        .catch((err) => {
          this.$store.dispatch('message/pushError', err)
        })
    },

    goToEntity(entity_idx) {
      this.$router.push({
        name: 'label-cls',
        params: {
          task_id: this.task_id.toString(),
          entity_idx: entity_idx.toString(),
        },
      })
    },

    reset() {
      this.dirty = false
      this.label = -1 // chosen label index
      this.showLabels = false // whether the label chooser is shown
      this.inLabelChooser = false // whether the cursor is in label chooser
    },
  },
  beforeRouteEnter(to, from, next) {
    fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
  },
  beforeRouteUpdate(to, from, next) {
    if (this.dirty) {
      this.saveChanges().then(() => {
        this.reset()
        fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
      })
    } else {
      this.reset()
      fetchTaskAndEntity(to.params.task_id, to.params.entity_idx, next)
    }
  },
  beforeRouteLeave(to, from, next) {
    if (this.dirty) {
      this.saveChanges().then(() => next())
    } else next()
  },
}
</script>

<style scoped>
#label-chooser {
  position: absolute;
  top: 50px;
  left: 5px;
  z-index: 1;
}
</style>
