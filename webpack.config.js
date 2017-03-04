const ExtractTextPlugin = require('extract-text-webpack-plugin')
const OptimizeCSSPlugin = require('optimize-css-assets-webpack-plugin')
const webpack = require('webpack')
const path = require('path')
const merge = require('webpack-merge')

const BUILD_VENDOR = process.env.BUILD_VENDOR
const PRODUCTION = process.env.NODE_ENV === 'production';
const DEBUG = process.env.NODE_ENV === 'development';

const baseConfig = {
  output: {
    path: path.resolve(__dirname, 'static'),
    filename: PRODUCTION ? '[name].[chunkhash:8].js' : '[name].js',
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: "css-loader",
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
    // new OptimizeCSSPlugin(),  // Production only
    // new webpack.optimize.UglifyJsPlugin(),  // Production only
  ],

  resolve: {
    modules: [
      'node_modules',
      path.resolve(__dirname, 'src')
    ]
  }
}

const appConfig = merge(baseConfig, {
  entry: {
    app: [path.resolve(__dirname, 'src/js/app.js')],
  },

  plugins: [

  ],
})

const vendorConfig = merge(baseConfig, {
  entry: {
    vendor: ['dropzone', 'file-saver'],
  },

  output: {
    library: '[name]_lib',
  },

  plugins: [
    new webpack.DllPlugin({
        path: path.resolve(__dirname, 'static', '[name]-manifest.json'),
        name: '[name]_[hash]',
    }),
  ],
})

if (!BUILD_VENDOR) {
  appConfig.plugins.push(
    new webpack.DllReferencePlugin({
      context: path.resolve(__dirname, 'static'),
      manifest: require(path.resolve(__dirname, 'static', 'vendor-manifest.json')),
    })
  )
  module.exports = appConfig
} else {
  module.exports = vendorConfig
}
