// Help automate webpack process
const path = require('path');

module.exports = {

    // Ensure that all files that are of type .js, .jsx, .ts, .tsx, .json don't need to be specified
    // when importing. Don't remove because code that is copied from original Valetudo will break
    resolve: {
    entry: './src/index.js', // your main file
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'bundle.js',
    },
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
    },
    module: {
        rules: [
        {
            test: /\.(js|jsx)$/,
            exclude: /node_modules/,
            use: 'babel-loader',
        },
        ],
    },
}