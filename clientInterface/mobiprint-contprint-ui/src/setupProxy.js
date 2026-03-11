const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    '/roborock',
    createProxyMiddleware({
      target: 'http://192.168.0.82',
      changeOrigin: true,
      pathRewrite: {
        '^/api1': '',
      },
    })
  );

  app.use(
    '/raspi',
    createProxyMiddleware({
      target: 'http://127.0.0.1:5000',
      changeOrigin: true,
      pathRewrite: {
        '^/api2': '',
      },
    })
  );
};