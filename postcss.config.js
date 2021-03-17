module.exports = {
  plugins: [
    require('postcss-import'),
    require('@tailwindcss/jit'),
    require('autoprefixer'),
    ...process.env.NODE_ENV === 'production'
      ? [require('cssnano')]
      : []
  ]
}