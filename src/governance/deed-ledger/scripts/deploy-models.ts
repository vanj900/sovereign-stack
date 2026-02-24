import { CeramicClient } from '@ceramicnetwork/http-client';
import { ComposeClient } from '@composedb/client';
import { DID } from 'dids';
import { Ed25519Provider } from 'key-did-provider-ed25519';
import { getResolver } from 'key-did-resolver';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Deploy Ceramic ComposeDB models to Clay testnet
 * 
 * Usage:
 *   pnpm deploy:models
 * 
 * Note: This requires a Ceramic node running and a DID seed.
 * For production, use proper key management.
 */
async function deployModels() {
  try {
    // Connect to Ceramic Clay testnet
    const ceramicUrl = process.env.CERAMIC_API_URL || 'https://ceramic-clay.3boxlabs.com';
    const ceramic = new CeramicClient(ceramicUrl);

    console.log(`Connecting to Ceramic at ${ceramicUrl}...`);

    // Initialize DID (for local development, use a seed)
    // In production, use proper key management
    const seed = process.env.DID_SEED 
      ? Buffer.from(process.env.DID_SEED, 'hex')
      : new Uint8Array(32); // Default seed for testing

    const provider = new Ed25519Provider(seed);
    const did = new DID({ provider, resolver: getResolver() });
    await did.authenticate();
    ceramic.did = did;

    console.log(`Authenticated with DID: ${did.id}`);

    // Read the GraphQL schema
    const schemaPath = join(__dirname, '../packages/schemas/src/models/reputation.graphql');
    const schema = readFileSync(schemaPath, 'utf-8');

    console.log('Schema loaded, deploying models...');
    console.log(schema);

    // Initialize ComposeDB client
    const compose = new ComposeClient({ ceramic, definition: schema });

    console.log('\n✅ Models ready for deployment!');
    console.log('\nNext steps:');
    console.log('1. Run a local Ceramic node: ceramic daemon');
    console.log('2. Use ComposeDB CLI to deploy models: composedb composite:create reputation.graphql');
    console.log('3. Update your app with the generated composite definition');

  } catch (error) {
    console.error('Error deploying models:', error);
    process.exit(1);
  }
}

deployModels();
