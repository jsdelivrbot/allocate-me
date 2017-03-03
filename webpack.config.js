const path = require('path')
const ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
  entry: path.resolve(__dirname, 'src/app.js'),

  output: {
    path: path.resolve(__dirname, 'static'),
    filename: 'bundle.js'
  },

  module: {
    rules: [
      {
        test: /\.css$/,
        use: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: "css-loader"
        })
      },
      {
        test: /\.js$/,
        exclude: [/node_modules/, /bower_components/],
        use: [{
          loader: 'babel-loader',
          options: {
            presets: ['es2015']
          }
        }],
      },
    ]
  },

  plugins: [
    new ExtractTextPlugin('styles.css'),
  ],

  resolve: {
    modules: [
      'node_modules',
      path.resolve(__dirname, 'src')
    ]
  }
}
