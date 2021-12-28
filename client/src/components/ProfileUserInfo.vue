<template>
  <div>
    <v-card>
      <v-card-title>用户信息</v-card-title>
      <v-card-text>
        <v-form ref="updateInfoForm">
          <v-row align="center">
            <v-col cols="3">用户名</v-col>
            <v-col v-if="!modify">{{ user.name }}</v-col>
            <v-col v-else>
              <v-text-field
                dense
                v-model="local_user.name"
                :rules="nameRules"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row align="center">
            <v-col cols="3">邮箱</v-col>
            <v-col v-if="!modify">{{ user.email }}</v-col>
            <v-col v-else>
              <v-text-field
                dense
                validate-on-blur
                :rules="emailRules"
                v-model="local_user.email"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row align="center">
            <v-col cols="3">用户类别</v-col>
            <v-col>{{ user.type === 'admin' ? '管理员' : '普通用户' }}</v-col>
          </v-row>
          <template v-if="modify">
            <v-row align="center">
              <v-col cols="3">新密码（可选）</v-col>
              <v-col>
                <v-text-field
                  :type="showNewPassword ? 'text' : 'password'"
                  dense
                  validate-on-blur
                  v-model="local_user.newPassword"
                  :rules="newPasswordRules"
                  :append-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  @click:append="showNewPassword = !showNewPassword"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row align="center">
              <v-col cols="3">确认新密码（可选）</v-col>
              <v-col>
                <v-text-field
                  :type="showNewPasswordConfirm ? 'text' : 'password'"
                  dense
                  validate-on-blur
                  v-model="local_user.newPasswordConfirm"
                  :rules="newPasswordConfirmRules"
                  :append-icon="
                    showNewPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'
                  "
                  @click:append="
                    showNewPasswordConfirm = !showNewPasswordConfirm
                  "
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row align="center">
              <v-col cols="3">原密码</v-col>
              <v-col>
                <v-text-field
                  :type="showOldPassword ? 'text' : 'password'"
                  dense
                  validate-on-blur
                  v-model="local_user.oldPassword"
                  :rules="oldPasswordRules"
                  :append-icon="showOldPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  @click:append="showOldPassword = !showOldPassword"
                ></v-text-field>
              </v-col>
            </v-row>
          </template>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="toggleModify">{{
          modify ? '取消' : '修改'
        }}</v-btn>
        <v-spacer></v-spacer>
        <v-btn v-if="modify" color="success" @click="submit">提交</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import NProgress from 'nprogress'
import { validateEmail } from '@/helpers/validators.js'

export default {
  props: {
    user: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      local_user: {
        id: this.user.id,
        name: this.user.name,
        email: this.user.email,
        oldPassword: '',
        newPassword: '',
        newPasswordConfirm: '',
      },

      nameRules: [
        (v) => !!v || '名字是必填项。',
        (v) => v.length <= 120 || '名字过长。',
      ],

      emailRules: [
        (v) => !!v || '邮箱是必填项。',
        (v) => v.length <= 120 || '邮箱过长。',
        (v) => validateEmail(v) || '请输入格式正确的邮箱。',
      ],

      newPasswordRules: [
        (v) => !v || v.length >= 8 || '密码长度至少应为 8 位。',
        (v) => !v || v.length <= 64 || '密码长度最多应为 64 位。',
        (v) =>
          !v ||
          (/[A-Za-z]/.test(v) &&
            /[0-9]/.test(v) &&
            /[ !"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]/.test(v)) ||
          '密码中应含有字母、数字和特殊字符。',
      ],

      newPasswordConfirmRules: [
        (v) =>
          (!v && !this.local_user.newPassword) ||
          v === this.local_user.newPassword ||
          '两次密码不一致，请检查。',
      ],

      oldPasswordRules: [
        (v) => !!v || '密码是必填项。',
        (v) => v.length >= 8 || '密码长度至少应为 8 位。',
        (v) => v.length <= 64 || '密码长度最多应为 64 位。',
      ],

      showOldPassword: false,
      showNewPassword: false,
      showNewPasswordConfirm: false,
      modify: false,
    }
  },

  methods: {
    toggleModify() {
      this.modify = !this.modify
      if (!this.modify) {
        this.local_user = {
          name: this.user.name,
          email: this.user.email,
          oldPassword: null,
          newPassword: null,
        }
      }
    },
    submit() {
      if (this.$refs.updateInfoForm.validate()) {
        this.updateInfo()
      }
    },
    updateInfo() {
      const payload = {
        id: this.user.id,
        data: {
          name: !this.local_user.name ? null : this.local_user.name,
          email: !this.local_user.email ? null : this.local_user.email,
          old_password: !this.local_user.oldPassword
            ? null
            : this.local_user.oldPassword,
          new_password: !this.local_user.newPassword
            ? null
            : this.local_user.newPassword,
        },
      }
      this.$store
        .dispatch('user/updateInfo', payload)
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '信息修改成功。')
          this.modify = false
          NProgress.done()
        })
        .catch((err) => {
          this.$store.dispatch('message/pushError', err)
        })
    },
  },
}
</script>

<style scoped></style>
