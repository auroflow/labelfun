import { helpers } from 'vuelidate/lib/validators'

export const passwordContainUpper = helpers.regex(
  'passwordContainUpper',
  /[A-Z]/
)

export const passwordContainLower = helpers.regex(
  'passwordContainLower',
  /[a-z]/
)

export const passwordContainNumber = helpers.regex(
  'passwordContainNumber',
  /[0-9]/
)

export const passwordContainSpecial = helpers.regex(
  'passwordContainSpecial',
  /[ !"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]/
)
