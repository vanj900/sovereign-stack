'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WagmiProvider } from 'wagmi';
import { wagmiConfig } from '../../lib/wagmi';
import { DIDAuthProvider } from '../../context/DIDContext';
import { useState, type ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <DIDAuthProvider>{children}</DIDAuthProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}
