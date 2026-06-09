import React from 'react';
import { Cpu, Maximize, Clock, ShieldCheck } from 'lucide-react';

const Features = () => {
  const features = [
    {
      icon: <Cpu size={32} color="var(--accent-cyan)" />,
      title: "AI-Powered CAD Automation",
      description: "Proprietary neural networks parse your raw engineering inputs and auto-generate complex CAD geometries with zero manual drafting."
    },
    {
      icon: <ShieldCheck size={32} color="var(--accent-green)" />,
      title: "Standards-Based Design",
      description: "Built-in compliance checking ensures all outputs adhere strict engineering standards (ASME BPE, cGMP) right out of the box."
    },
    {
      icon: <Clock size={32} color="var(--accent-cyan)" />,
      title: "Instant Export & Iteration",
      description: "Generate drafts in seconds. Catch an error in your URS? Update the text and regenerate the entire DXF/DWG file instantly."
    },
    {
      icon: <Maximize size={32} color="var(--accent-green)" />,
      title: "Scalable Across Industries",
      description: "Whether you're mapping pharmaceutical bioreactors or generating architectural floor plans from satellite data, AutoCHAD adapts."
    }
  ];

  return (
    <section id="features" className="section" style={{ position: 'relative' }}>
      <div className="container">
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>What We Do</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto', fontSize: '1.1rem' }}>
            Transforming weeks of manual drafting into seconds of automated generation.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '30px'
        }}>
          {features.map((f, i) => (
            <div key={i} className="glass-panel" style={{
              padding: '30px',
              transition: 'transform 0.3s ease, background 0.3s ease',
              cursor: 'pointer'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)';
              e.currentTarget.style.background = 'rgba(25, 25, 35, 0.8)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.background = 'var(--glass-bg)';
            }}
            >
              <div style={{ marginBottom: '20px' }}>{f.icon}</div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '12px' }}>{f.title}</h3>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
