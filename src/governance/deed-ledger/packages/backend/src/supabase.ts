import { createClient, SupabaseClient } from '@supabase/supabase-js';

let supabaseClient: SupabaseClient | null = null;

export function initSupabase(): SupabaseClient {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    throw new Error('SUPABASE_URL and SUPABASE_KEY must be set in environment');
  }

  if (!supabaseClient) {
    supabaseClient = createClient(supabaseUrl, supabaseKey);
  }

  return supabaseClient;
}

export function getSupabase(): SupabaseClient {
  if (!supabaseClient) {
    return initSupabase();
  }
  return supabaseClient;
}

// Example: Index a deed to Supabase for faster queries
export async function indexDeed(deed: {
  id: string;
  controller: string;
  type: string;
  createdAt: string;
}) {
  const supabase = getSupabase();
  
  const { data, error } = await supabase
    .from('deeds')
    .insert([deed]);

  if (error) {
    console.error('Error indexing deed:', error);
    throw error;
  }

  return data;
}
