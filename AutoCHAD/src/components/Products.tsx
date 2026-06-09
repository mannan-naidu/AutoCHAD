import React, { useState } from 'react';
import { Upload, Map as MapIcon, Aperture, Download } from 'lucide-react';

const Products = () => {
  const [activeTab, setActiveTab] = useState('pharma');
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiResult, setApiResult] = useState<any>(null);

  const generateCAD = async () => {
    if (!inputText) return alert("Please enter specifications first!");
    
    setIsLoading(true);
    setApiResult(null);
    try {
      const response = await fetch('http://localhost:8000/generate-dxf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_type: 'text', content: inputText })
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }
      setApiResult(data);
    } catch (err: any) {
      alert("API Error: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="products" className="section" style={{ backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
      <div className="container">
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>Our Core <span className="text-gradient-cyan">Products</span></h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto', fontSize: '1.1rem' }}>
            Specialized AI engines trained on industry-specific drafting standards.
          </p>
        </div>

        {/* Tab Selection */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '40px' }}>
          <button 
            className={`btn ${activeTab === 'pharma' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('pharma')}
          >
            <Aperture size={20} /> PharmaCAD
          </button>
          <button 
            className={`btn ${activeTab === 'geo' ? 'btn-green' : 'btn-secondary'}`}
            onClick={() => setActiveTab('geo')}
          >
            <MapIcon size={20} /> GeoCAD
          </button>
        </div>

        {/* Product Content Container */}
        <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
          {activeTab === 'pharma' ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 1.5fr', minHeight: '500px' }}>
              {/* Product Info */}
              <div style={{ padding: '40px', borderRight: '1px solid var(--glass-border)' }}>
                <div style={{ display: 'inline-block', padding: '6px 12px', background: 'rgba(0, 240, 255, 0.1)', color: 'var(--accent-cyan)', borderRadius: '12px', marginBottom: '20px', fontSize: '0.85rem', fontWeight: 600 }}>Pharmaceutical Manufacturing</div>
                <h3 style={{ fontSize: '2rem', marginBottom: '20px' }}>PharmaCAD Engine</h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '30px' }}>
                  AI engine that converts URS (User Requirement Specification) documents and hand-drawn sketches into precise P&ID diagrams and equipment layouts.
                </p>
                <ul style={{ listStyle: 'none', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{width: 8, height: 8, background:'var(--accent-cyan)', borderRadius: '50%'}}></div> Hand-drawn sketch recognition</li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{width: 8, height: 8, background:'var(--accent-cyan)', borderRadius: '50%'}}></div> ASME BPE and cGMP compliance check</li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{width: 8, height: 8, background:'var(--accent-cyan)', borderRadius: '50%'}}></div> Auto-generates Instrumentation & BOM</li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{width: 8, height: 8, background:'var(--accent-cyan)', borderRadius: '50%'}}></div> Direct DXF/DWG Export</li>
                </ul>
              </div>
              
              {/* Interactive Demo Interface */}
              <div style={{ padding: '40px', background: 'rgba(0,0,0,0.2)', display: 'flex', flexDirection: 'column' }}>
                <h4 style={{ marginBottom: '20px', color: '#fff' }}>Interactive Demo</h4>
                
                {/* Upload Area */}
                <div style={{ 
                  border: '2px dashed var(--glass-border)', 
                  borderRadius: '12px', 
                  padding: '30px', 
                  textAlign: 'center',
                  marginBottom: '10px',
                  cursor: 'pointer',
                  transition: 'border-color 0.3s'
                }}
                onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--accent-cyan)'}
                onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--glass-border)'}
                >
                  <Upload size={32} color="var(--text-secondary)" style={{ margin: '0 auto 10px' }} />
                  <p>Drag & Drop URS pdf or sketch image here</p>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Supports: .pdf, .png, .jpg</span>
                </div>

                <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '10px', fontSize: '0.9rem' }}>
                  — OR —
                </div>

                {/* Text Input Area */}
                <textarea 
                  placeholder="Paste engineering specifications or URS text here..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  style={{
                    width: '100%',
                    height: '100px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: '8px',
                    padding: '12px',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-main)',
                    resize: 'none',
                    marginBottom: '20px',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = 'var(--accent-cyan)'}
                  onBlur={(e) => e.currentTarget.style.borderColor = 'var(--glass-border)'}
                ></textarea>

                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
                  <button className="btn btn-primary" onClick={generateCAD} disabled={isLoading}>
                    {isLoading ? "Processing via AI..." : "Generate CAD"}
                  </button>
                </div>

                {/* Preview Window Placeholder */}
                <div style={{
                  flex: 1,
                  background: '#000',
                  borderRadius: '8px',
                  border: '1px solid var(--glass-border)',
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                  padding: '20px',
                  wordBreak: 'break-all'
                 }}>
                  <div style={{
                    position: 'absolute',
                    top: 0, left: 0, right: 0, bottom: 0,
                    backgroundImage: `linear-gradient(rgba(0, 240, 255, 0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 240, 255, 0.2) 1px, transparent 1px)`,
                    backgroundSize: '30px 30px',
                    opacity: 0.5
                  }}></div>
                  <div style={{ position: 'relative', zIndex: 1, color: 'var(--text-secondary)' }}>
                    {apiResult ? (
                      <div>
                        <p style={{ color: 'var(--accent-green)', fontWeight: 'bold' }}>Success!</p>
                        <p>DXF saved at: {apiResult.file_path}</p>
                        <pre style={{ fontSize: '0.75rem', marginTop: '10px', textAlign: 'left', color: '#fff', maxHeight: '150px', overflowY: 'auto' }}>
                          {JSON.stringify(apiResult.parsed_schema, null, 2)}
                        </pre>
                      </div>
                    ) : (
                      "Output Preview Empty"
                    )}
                  </div>
                </div>

              </div>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 1.5fr', minHeight: '500px' }}>
              {/* GeoCAD Info */}
              <div style={{ padding: '40px', borderRight: '1px solid var(--glass-border)' }}>
                <div style={{ display: 'inline-block', padding: '6px 12px', background: 'rgba(57, 255, 20, 0.1)', color: 'var(--accent-green)', borderRadius: '12px', marginBottom: '20px', fontSize: '0.85rem', fontWeight: 600 }}>Architectural CAD Generator</div>
                <h3 style={{ fontSize: '2rem', marginBottom: '20px' }}>GeoCAD Engine</h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '30px' }}>
                  Convert selected geographic areas from maps directly into precise architectural CAD drawings and site plans.
                </p>
                <ul style={{ listStyle: 'none', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{width: 8, height: 8, background:'var(--accent-green)', borderRadius: '50%'}}></div> Interactive high-res map selector</li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{width: 8, height: 8, background:'var(--accent-green)', borderRadius: '50%'}}></div> Building outline and contour extraction</li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{width: 8, height: 8, background:'var(--accent-green)', borderRadius: '50%'}}></div> Automatic plot boundary tracing</li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{width: 8, height: 8, background:'var(--accent-green)', borderRadius: '50%'}}></div> Real-world dimensional scaling</li>
                </ul>
              </div>

              {/* GeoCAD Demo Interface */}
              <div style={{ padding: '40px', background: 'rgba(0,0,0,0.2)', display: 'flex', flexDirection: 'column' }}>
                <div style={{ flex: 1, background: '#111', borderRadius: '12px', border: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '20px' }}>
                  <MapIcon size={48} color="var(--accent-green)" opacity={0.5} />
                  <p style={{ color: 'var(--text-secondary)' }}>Map Selector Interface Placeholder</p>
                  <button className="btn btn-green">Select Region to Generate</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Products;
