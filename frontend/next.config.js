/** @type {import('next').NextConfig} */
const nextConfig = {};

module.exports = {
  async headers() {
      return [
          {
              source: '/(.*)',
              headers: [
                  { key: 'Access-Control-Allow-Origin', value: '*' },
                  { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PUT,DELETE,POST' },
                  { key: 'Access-Control-Allow-Headers', value: 'Content-Type,Authorization' },
              ],
          },
      ];
  },
};


