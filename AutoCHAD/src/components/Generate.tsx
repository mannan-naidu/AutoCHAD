import React, { useState } from 'react';
import { UploadCloud, Zap, Download, AlertCircle, Loader } from 'lucide-react';

type Status = 'idle' | 'loading' | 'success' | 'error';

const API_BASE = import.meta.env.VITE_API_URL ?? '/api';

const Generate = () => {
  const [inputText, setInputText] = useState('');
  const [status, setStatus] = useState<Status>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [downloadUrl, setDownloadUrl] = useState('');
  const [filename, setFilename] = useState('');

  const handleGenerate = async () => {
    if (!inputText.trim()) return;
    setStatus('loading');
    setErrorMsg('');
    setDownloadUrl('');

    try {
      const res = await fetch(`${API_BASE}/generate-dxf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_type: 'text', content: inputText }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error ?? `Server error ${res.status}`);
      }

      const blob = await res.blob();
      const disposition = res.headers.get('content-disposition') ?? '';
      const match = disposition.match(/filename="?([^"]+)"?/);
      const fname = match ? match[1] : 'autochad_output.dxf';

      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
      setFilename(fname);
      setStatus('success');
    } catch (err: any) {
      setErrorMsg(err.message ?? 'Unknown error');
      setStatus('error');
    }
  };

  return (
    <section className="section" style={{ minHeight: '100vh', paddingTop: '120px' }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>
            Generate Your <span className="text-gradient-cyan">P&amp;ID Drawing</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
            Describe your process system in plain English and get a production-ready DXF file.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '32px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
            Process Description
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="e.g. A pharmaceutical water purification system with a storage tank, two centrifugal pumps in parallel, pressure sensors, flow meters, and a UV steriliser..."
            rows={8}
            style={{
              width: '100%',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid var(--glass-border)',
              borderRadius: '8px',
              padding: '16px',
              color: 'var(--text-primary)',
              fontFamily: 'var(--font-main)',
              fontSize: '0.95rem',
              resize: 'vertical',
              outline: 'none',
            }}
          />

          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={status === 'loading' || !inputText.trim()}
            style={{ marginTop: '24px', width: '100%', padding: '16px', fontSize: '1.05rem',
                     opacity: status === 'loading' ? 0.7 : 1 }}
          >
            {status === 'loading' ? (
              <><Loader size={18} style={{ animation: 'spin 1s linear infinite' }} /> Generating DXF…</>
            ) : (
              <><Zap size={18} /> Generate DXF</>
            )}
          </button>

          {status === 'error' && (
            <div style={{
              marginTop: '20px', padding: '16px', borderRadius: '8px',
              background: 'rgba(255,50,50,0.1)', border: '1px solid rgba(255,50,50,0.3)',
              display: 'flex', gap: '10px', alignItems: 'flex-start',
            }}>
              <AlertCircle size={18} color="#ff5050" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span style={{ color: '#ff8080', fontSize: '0.9rem' }}>{errorMsg}</span>
            </div>
          )}

          {status === 'success' && downloadUrl && (
            <div style={{
              marginTop: '20px', padding: '20px', borderRadius: '8px',
              background: 'rgba(57,255,20,0.08)', border: '1px solid rgba(57,255,20,0.3)',
              textAlign: 'center',
            }}>
              <p style={{ color: 'var(--accent-green)', marginBottom: '16px', fontWeight: 600 }}>
                DXF generated successfully!
              </p>
              <a
                href={downloadUrl}
                download={filename}
                className="btn btn-green"
                style={{ display: 'inline-flex', gap: '8px' }}
              >
                <Download size={18} /> Download {filename}
              </a>
            </div>
          )}
        </div>

        <p style={{ textAlign: 'center', marginTop: '24px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          Output complies with ASME/GMP P&amp;ID standards. Open in AutoCAD, LibreCAD, or any DXF viewer.
        </p>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </section>
  );
};

export default Generate;
