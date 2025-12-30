'use client';

import { WagmiProvider, createConfig, http } from 'wagmi';
import { getDefaultConfig, RainbowKitProvider } from '@rainbow-me/rainbowkit';
import { mainnet, sepolia, hardhat } from 'wagmi/chains';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@rainbow-me/rainbowkit/styles.css';

// Validate WalletConnect project ID
const walletConnectProjectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID;
if (!walletConnectProjectId || walletConnectProjectId === 'your-project-id') {
  console.warn('⚠️ NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID is not set or is a placeholder. Wallet connection may not work.');
}

const config = getDefaultConfig({
  appName: 'ShotMint',
  projectId: walletConnectProjectId || 'your-project-id', // Will show error if not set
  chains: [mainnet, sepolia, hardhat],
  ssr: true,
});

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>{children}</RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}

