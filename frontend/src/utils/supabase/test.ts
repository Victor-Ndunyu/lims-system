import { createClient } from '@/utils/supabase/client';

async function testSupabaseConnection() {
  try {
    const supabase = createClient();
    
    // Test the connection by fetching from a simple table or checking auth
    const { data, error } = await supabase
      .from('todos')
      .select('*')
      .limit(1);

    if (error) {
      console.error('Supabase connection error:', error);
      return { success: false, error: error.message };
    }

    console.log('✓ Supabase connection successful');
    console.log('Data:', data);
    return { success: true, data };
  } catch (err) {
    console.error('Error testing Supabase connection:', err);
    return { 
      success: false, 
      error: err instanceof Error ? err.message : 'Unknown error' 
    };
  }
}

export default testSupabaseConnection;
