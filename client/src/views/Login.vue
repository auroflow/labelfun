<template>
  <v-container fluid fill-height>
    <v-row class="align-center justify-center">
      <v-col>
        <v-card width="400" class="mx-auto my-5">
          <v-form refs="loginForm">
            <v-card-title>
              <h1 class="display-1">登录</h1>
            </v-card-title>
            <v-card-text>
              <v-text-field
                label="邮箱"
                type="email"
                v-model="email"
                :error-messages="emailErrors"
                @blur="$v.email.$touch()"
                prepend-icon="mdi-account-circle"
                required
              />
              <v-text-field
                :type="showPassword ? 'text' : 'password'"
                label="密码"
                v-model="password"
                :error-messages="passwordErrors"
                @blur="$v.password.$touch()"
                prepend-icon="mdi-lock"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword"
                @keyup.enter="submit"
                required
              />
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
              <v-btn color="secondary" :to="{ name: 'signup' }">注册</v-btn>
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="submit">登录</v-btn>
            </v-card-actions>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { email, required, minLength, maxLength } from 'vuelidate/lib/validators'
import { validationMixin } from 'vuelidate'
import NProgress from 'nprogress'

export default {
  mixins: [validationMixin],

  data() {
    return {
      email: '',
      password: '',
      invitation: '',
      error: null,
      showPassword: false,
    }
  },

  computed: {
    emailErrors() {
      const errors = []
      if (!this.$v.email.$dirty) return errors
      !this.$v.email.required && errors.push('邮箱为必填项。')
      !this.$v.email.email && errors.push('请输入正确格式的邮箱。')
      !this.$v.email.maxLength && errors.push('邮箱过长。')
      return errors
    },
    passwordErrors() {
      const errors = []
      if (!this.$v.password.$dirty) return errors
      !this.$v.password.required && errors.push('密码为必填项。')
      !this.$v.password.minLength && errors.push('密码至少包含 8 位。')
      !this.$v.password.maxLength && errors.push('密码最多包含 32 位。')
      return errors
    },
  },

  methods: {
    submit() {
      this.$v.$touch()
      if (!this.$v.$invalid) {
        this.login()
      }
    },
    login() {
      NProgress.start()

      this.$store
        .dispatch('user/login', {
          email: this.email,
          password: this.password,
        })
        .then(() => {
          this.$store.dispatch('message/pushSuccess', '登录成功。')
          this.$router.push({ name: 'home' })
        })
        .catch((err) => {
          this.$store.dispatch('message/pushError', err)
          this.password = ''
          this.$v.$reset()
        })
    },
  },

  validations: {
    email: {
      required,
      email,
      maxLength: maxLength(120),
    },
    password: {
      required,
      minLength: minLength(8),
      maxLength: maxLength(32),
    },
  },
}
</script>

<style scoped></style>
