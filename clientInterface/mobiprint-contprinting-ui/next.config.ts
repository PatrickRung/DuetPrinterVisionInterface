import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

const path = require('path');
require('dotenv').config({
  // Load external .env
  path: path.resolve(__dirname, '../../.env'),
});

module.exports = {
  reactStrictMode: true,
};

export default nextConfig;
