import { useEffect, useState } from 'react';
import testSupabaseConnection from '@/utils/supabase/test';

export default function TestPage() {
  const [status, setStatus] = useState('Testing...');
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    testSupabaseConnection().then((result) => {
      if (result.success) {
        setStatus('✓ Connection successful');
        setData(result.data);
      } else {
        setStatus('✗ Connection failed');
        setError(result.error || 'Unknown error');
      }
    });
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Supabase Connection Test</h1>
      <p>Status: {status}</p>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {data && (
        <div>
          <p>Sample data retrieved:</p>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
