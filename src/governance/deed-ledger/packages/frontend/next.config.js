/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // PWA configuration
  experimental: {
    // Enable Server Components
  },

  webpack: (config) => {
    // Stub optional wagmi connector peer dependencies that are not installed
    config.resolve.fallback = {
      ...config.resolve.fallback,
      'porto/internal': false,
      '@safe-global/safe-apps-sdk': false,
      '@safe-global/safe-apps-provider': false,
      '@coinbase/wallet-sdk': false,
      '@metamask/sdk': false,
      '@walletconnect/ethereum-provider': false,
      '@base-org/account': false,
    };
    return config;
  },
  
  // For PWA, you'd add next-pwa here in production
  // const withPWA = require('next-pwa')({ dest: 'public' })
  // module.exports = withPWA(nextConfig)
}

module.exports = nextConfig
