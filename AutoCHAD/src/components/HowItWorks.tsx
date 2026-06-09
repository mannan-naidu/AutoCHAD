import React from 'react';
import { FileUp, Cpu, PencilRuler, Download } from 'lucide-react';

const HowItWorks = () => {
  const steps = [
    { icon: <FileUp size={40} />, title: "1. Upload / Select Input", desc: "Drag & drop your URS file, sketch, or select a map area." },
    { icon: <Cpu size={40} />, title: "2. AI Interpretation", desc: "Our engine uses NLP and Computer Vision to parse your engineering intent." },
    { icon: <PencilRuler size={40} />, title: "3. Standards Application", desc: "Strict compliance rules (ASME, cGMP) are mathematically applied to the draft." },
    { icon: <Download size={40} />, title: "4. Output Generation", desc: "Instantly download your production-ready DXF or DWG file." }
  ];

  return (
    <section className="section">
      <div className="container">
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>How It Works</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto', fontSize: '1.1rem' }}>
            A streamlined 4-step pipeline designed for zero-friction workflows.
          </p>
        </div>

        <div style={{ 
          display: 'flex', 
          flexDirection: 'row', 
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '20px',
          position: 'relative'
        }}>
          {/* Connector Line (visible on desktop) */}
          <div style={{
            position: 'absolute',
            top: '50px',
            left: '10%',
            right: '10%',
            height: '2px',
            background: 'var(--glass-border)',
            zIndex: 0
          }} className="hide-on-mobile"></div>

          {steps.map((step, idx) => (
            <div key={idx} style={{ flex: '1 1 200px', textAlign: 'center', position: 'relative', zIndex: 1 }}>
              <div style={{
                width: '100px',
                height: '100px',
                background: 'var(--bg-secondary)',
                border: '2px solid var(--accent-cyan)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                color: 'var(--accent-cyan)',
                boxShadow: '0 0 20px rgba(0, 240, 255, 0.15)'
              }}>
                {step.icon}
              </div>
              <h4 style={{ fontSize: '1.2rem', marginBottom: '10px' }}>{step.title}</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', padding: '0 10px' }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
