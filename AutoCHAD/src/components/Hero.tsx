import React from 'react';
import { Link } from 'react-router-dom';
import { UploadCloud, Zap } from 'lucide-react';

const Hero = () => {
  return (
    <section className="section" style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      paddingTop: '120px' // for fixed navbar offset
    }}>
      <div className="container" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '60px',
        alignItems: 'center'
      }}>
        {/* Left Content */}
        <div className="animate-fade-in">
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 16px',
            background: 'var(--glass-bg)',
            border: '1px solid var(--accent-cyan)',
            borderRadius: '20px',
            marginBottom: '24px',
            fontSize: '0.9rem',
            color: 'var(--accent-cyan)'
          }}>
            <Zap size={16} /> <span>v2.0 AI Engine is Live</span>
          </div>
          
          <h1 style={{
            fontSize: '3.5rem',
            marginBottom: '24px',
            lineHeight: 1.1
          }}>
            Turn Inputs into <br/>
            <span className="text-gradient-cyan">CAD Designs</span> Instantly with AI.
          </h1>
          
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '1.2rem',
            marginBottom: '40px',
            maxWidth: '90%'
          }}>
            From URS documents to maps — AutoCHAD generates production-ready CAD drawings in seconds. Faster, smarter, and incredibly accurate.
          </p>

          <div style={{ display: 'flex', gap: '20px' }}>
            <Link to="/generate" className="btn btn-primary pulse-primary" style={{ padding: '16px 32px', fontSize: '1.1rem' }}>
              Get Started
            </Link>
            <Link to="/generate" className="btn btn-secondary" style={{ padding: '16px 32px', fontSize: '1.1rem' }}>
              <UploadCloud size={20} />
              Try Demo
            </Link>
          </div>
          
          <div style={{ marginTop: '40px', display: 'flex', gap: '24px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Zap size={16} color="var(--accent-green)" /> 80% Faster</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Zap size={16} color="var(--accent-green)" /> Error-free Generation</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Zap size={16} color="var(--accent-green)" /> DXF/DWG Export</span>
          </div>
        </div>

        {/* Right Content - Visual Mockup */}
        <div className="glass-panel animate-fade-in" style={{
          padding: '24px',
          height: '500px',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden',
          animationDelay: '0.3s'
        }}>
          {/* Blueprint background grid for the card */}
          <div style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundImage: `linear-gradient(rgba(0, 240, 255, 0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0, 240, 255, 0.1) 1px, transparent 1px)`,
            backgroundSize: '20px 20px',
            zIndex: 0,
            opacity: 0.5
          }}></div>

          <div style={{ position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px' }}>
            <span style={{ fontFamily: 'var(--font-heading)', color: 'var(--accent-cyan)' }}>Processing: Hand_Sketch_Tank.png</span>
            <span style={{ color: 'var(--accent-green)' }}>Status: Complete</span>
          </div>
          
          {/* Conceptual Flow Visual */}
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-around', position: 'relative', zIndex: 1 }}>
            
            {/* Input Form Box */}
            <div style={{ border: '2px dashed var(--text-secondary)', padding: '20px', borderRadius: '12px', textAlign: 'center' }}>
              <div style={{ width: '100px', height: '100px', border: '1px solid var(--text-secondary)', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Sketch</span>
              </div>
            </div>

            {/* AI Arrow */}
            <div style={{ color: 'var(--accent-cyan)' }}>
              <Zap size={32} />
            </div>

            {/* Output Form Box */}
            <div style={{ border: '2px solid var(--accent-cyan)', padding: '20px', borderRadius: '12px', textAlign: 'center', boxShadow: '0 0 20px rgba(0,240,255,0.2)' }}>
              <div style={{ width: '100px', height: '100px', background: 'rgba(0,240,255,0.1)', border: '1px solid var(--accent-cyan)', margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                {/* Simulated precise lines */}
                <div style={{ position: 'absolute', top: '10%', left: '10%', right: '10%', height: '1px', background: 'var(--accent-cyan)' }}></div>
                <div style={{ position: 'absolute', bottom: '10%', left: '10%', right: '10%', height: '1px', background: 'var(--accent-cyan)' }}></div>
                <div style={{ position: 'absolute', top: '10%', bottom: '10%', left: '10%', width: '1px', background: 'var(--accent-cyan)' }}></div>
                <div style={{ position: 'absolute', top: '10%', bottom: '10%', right: '10%', width: '1px', background: 'var(--accent-cyan)' }}></div>
                <span style={{ color: 'var(--accent-cyan)', fontSize: '0.8rem', fontWeight: 700, zIndex: 2 }}>P&ID DXF</span>
              </div>
            </div>
            
          </div>
          
        </div>
      </div>
    </section>
  );
};

export default Hero;
