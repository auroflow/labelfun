<template>
  <v-container fluid fill-height>
    <v-row class="align-center justify-center">
      <v-col>
        <v-card width="400" class="mx-auto my-5">
          <v-card-title>
            <h1 class="display-1">注册</h1>
          </v-card-title>
          <v-card-text>
            <v-form ref="signupForm">
              <v-text-field
                label="名字"
                type="text"
                v-model="name"
                :rules="nameRules"
                required
                validate-on-blur
              ></v-text-field>
              <v-text-field
                label="邮箱"
                type="email"
                v-model="email"
                :rules="emailRules"
                required
                validate-on-blur
              ></v-text-field>
              <v-text-field
                :type="showPassword ? 'text' : 'password'"
                label="密码"
                v-model="password"
                :rules="passwordRules"
                required
                validate-on-blur
                prepend-icon="mdi-lock"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword"
              />
              <v-text-field
                :type="showRepeatPassword ? 'text' : 'password'"
                label="重复密码"
                v-model="repeatPassword"
                :rules="repeatPasswordRules"
                required
                validate-on-blur
                prepend-icon="mdi-lock"
                :append-icon="showRepeatPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showRepeatPassword = !showRepeatPassword"
              />
              <v-text-field
                :type="showInvitation ? 'text' : 'password'"
                label="邀请码"
                v-model="invitationCode"
                :rules="invitationCodeRules"
                required
                validate-on-blur
                prepend-icon="mdi-account-plus"
                :append-icon="showInvitation ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showInvitation = !showInvitation"
              />
            </v-form>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="submit" color="primary">注册</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { email, required, minLength, maxLength } from 'vuelidate/lib/validators'
import { validationMixin } from 'vuelidate'
import { validateEmail } from '@/helpers/validators.js'

export default {
  mixins: [validationMixin],

  data() {
    return {
      name: '',
      email: '',
      password: '',
      repeatPassword: '',
      invitationCode: '',

      nameRules: [
        (v) => !!v || '名字是必填项。',
        (v) => v.length <= 120 || '名字过长。',
      ],
      emailRules: [
        (v) => !!v || '邮箱是必填项。',
        (v) => v.length <= 120 || '邮箱过长。',
        (v) => validateEmail(v) || '请输入格式正确的邮箱。',
      ],
      passwordRules: [
        (v) => !!v || '密码是必填项。',
        (v) => v.length >= 8 || '密码长度至少应为 8 位。',
        (v) => v.length <= 64 || '密码长度最多应为 64 位。',
        (v) =>
          (/[A-Za-z]/.test(v) &&
            /[0-9]/.test(v) &&
            /[ !"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]/.test(v)) ||
          '密码中应含有字母、数字和特殊字符。',
      ],
      repeatPasswordRules: [
        (v) => !!v || '重复密码是必填项。',
        (v) => v === this.password || '两次密码不一致，请检查。',
      ],
      invitationCodeRules: [(v) => !!v || '邀请码是必填项。'],

      showPassword: false,
      showRepeatPassword: false,
      showInvitation: false,
    }
  },

  methods: {
    submit() {
      if (this.$refs.signupForm.validate()) {
        this.signup()
      }
    },
    signup() {
      this.$store
        .dispatch('user/signup', {
          name: this.name,
          email: this.email,
          password: this.password,
          invitation: this.invitationCode,
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '注册成功，请登录。')
          this.$router.push({ name: 'login' })
        })
        .catch((err) => {
          this.$store.dispatch('message/pushError', err)
        })
    },
  },

  validations: {
    email: {
      required,
      email,
    },
    password: {
      required,
      minLength: minLength(6),
      maxLength: maxLength(16),
    },
  },
}
</script>

<style scoped></style>
