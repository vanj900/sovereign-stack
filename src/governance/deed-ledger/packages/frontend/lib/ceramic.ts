import { CeramicClient } from '@ceramicnetwork/http-client';
import { ComposeClient } from '@composedb/client';

import definition from '../__generated__/definition';

export const ceramic = new CeramicClient(
  process.env.NEXT_PUBLIC_CERAMIC_URL || 'https://ceramic-clay.3boxlabs.com'
);

export const composeClient = new ComposeClient({
  ceramic,
  definition,
});
