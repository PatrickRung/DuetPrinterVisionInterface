const { createProxyMiddleware } = require('http-proxy-middleware');


/*
  IMPORTANT
  Anytime you setup on a different network you will need to change the IP accordingly
  for both roborock and raspberry pi. Currently theres no constants holding the system
  however (thakfully) you only need to change them here! (front end does a lot of orchestration
  thus changing IP elswhere is for second passthrough!
*/
module.exports = function (app) {
  app.use(
    '/roborock',
    createProxyMiddleware({
      target: 'http://192.168.0.82',
      changeOrigin: true,
      pathRewrite: {
        '^/roborock': '',
      },
    })
  );

  // Test flask server generally uses port 5000
  app.use(
    '/raspi',
    createProxyMiddleware({
      target: 'http://192.168.0.207:5000',
      changeOrigin: true,
      pathRewrite: {
        '^/raspi': '',
      },
    })
  );
};