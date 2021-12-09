// vue.config.js

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */

module.exports = {
  transpileDependencies: ['vuetify'],
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
      },
      '/upload': {
        target: '',
        pathRewrite: { '^/upload': '' },
      },
    },
  },
}
