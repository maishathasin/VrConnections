const path = require('path');

module.exports = {
  entry: 'script.js', // Your main JS file
  output: {
    filename: 'bundle.js', // Output bundle file
    path: path.resolve(__dirname, 'dist'), // Directory for the output
  },
  module: {
    rules: [
      {
        test: /\.js$/, // For JavaScript files
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader', // To transpile ES6 and above
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  }
};
