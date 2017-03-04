const ExtractTextPlugin = require('extract-text-webpack-plugin')
const OptimizeCSSPlugin = require('optimize-css-assets-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const webpack = require('webpack')
const path = require('path')
const merge = require('webpack-merge')

const BUILD_VENDOR = process.env.BUILD_VENDOR
const PRODUCTION = process.env.NODE_ENV === 'production'
const DEBUG = process.env.NODE_ENV === 'development'

const INPUT_PATH = path.join(__dirname, 'src/')
const OUTPUT_PATH = path.join(__dirname, 'dist/')

const baseConfig = {
  output: {
    path: OUTPUT_PATH,
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: 'css-loader',
        })
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        use: 'url-loader?limit=8192',
      },
      {
        test: /\.js$/,
        exclude: [/node_modules/],
        use: [{
          loader: 'babel-loader',
          options: {
            presets: ['es2015'],
            compact: true,
          }
        }],
      },
    ]
  },

  plugins: [
    new ExtractTextPlugin(PRODUCTION ? '[name].[contenthash:8].css' : '[name].css'),
  ],

  resolve: {
    modules: [
      'node_modules',
      INPUT_PATH,
    ]
  }
}

if (PRODUCTION) {
  const uglifyPlugins = [
    new webpack.optimize.UglifyJsPlugin(),
    new OptimizeCSSPlugin(),
  ]
  baseConfig.plugins = baseConfig.plugins.concat(uglifyPlugins)
}

const appConfig = merge(baseConfig, {
  entry: {
    app: [path.join(INPUT_PATH, 'app.js')],
  },
  output: {
    filename: PRODUCTION ? '[name].[chunkhash:8].js' : '[name].js',
  }
})

const vendorConfig = merge(baseConfig, {
  entry: {
    vendor: ['dropzone', 'file-saver'],
  },

  output: {
    library: '[name]_lib',
    filename: '[name].dll.js',
  },

  plugins: [
    new webpack.DllPlugin({
        path: path.join(OUTPUT_PATH, '[name]-manifest.json'),
        name: '[name]_[hash]',
    }),
  ],
})

if (!BUILD_VENDOR) {
  appConfig.plugins = appConfig.plugins.concat([
    new webpack.DllReferencePlugin({
      context: OUTPUT_PATH,
      manifest: require(path.join(OUTPUT_PATH, 'vendor-manifest.json')),
    }),
    new HtmlWebpackPlugin({
      template: path.join(INPUT_PATH, 'index.html'),
      minify: PRODUCTION ? {
        collapseWhitespace: true,
      } : false,
    }),
  ])
  module.exports = appConfig
} else {
  module.exports = vendorConfig
}
