import { useEffect, useState } from 'react';
import testBackendConnection from '@/utils/supabase/test';

export default function TestPage() {
  const [status, setStatus] = useState('Testing backend connection...');
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    testBackendConnection().then((result) => {
      if (result.success) {
        setStatus('✓ Backend connection successful');
        setData(result.data);
      } else {
        setStatus('✗ Backend connection failed');
        setError(result.error || 'Unknown error');
      }
    });
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Backend Connection Test</h1>
      <p>Status: {status}</p>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {data && (
        <div>
          <p>Backend response:</p>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
