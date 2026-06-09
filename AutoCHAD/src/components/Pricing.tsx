import React from 'react';
import { Check } from 'lucide-react';

const Pricing = () => {
  return (
    <section id="pricing" className="section">
      <div className="container">
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>Transparent Pricing</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Scale your generation needs predictably.</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', alignItems: 'center' }}>
          {/* Free Tier */}
          <div className="glass-panel" style={{ padding: '40px' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Pilot</h3>
            <div style={{ fontSize: '3rem', fontWeight: 700, marginBottom: '20px' }}>$0<span style={{ fontSize: '1rem', color: 'var(--text-secondary)', fontWeight: 400 }}>/mo</span></div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '30px' }}>Perfect for evaluating the AI generation quality.</p>
            <ul style={{ listStyle: 'none', marginBottom: '40px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-cyan)" /> 5 Exports per month</li>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-cyan)" /> Standard CAD templates</li>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-cyan)" /> Basic NLP parsing</li>
            </ul>
            <button className="btn btn-secondary" style={{ width: '100%' }}>Start Free</button>
          </div>

          {/* Pro Tier */}
          <div className="glass-panel" style={{ padding: '50px 40px', border: '2px solid var(--accent-cyan)', position: 'relative', transform: 'scale(1.05)' }}>
            <div style={{ position: 'absolute', top: -15, left: '50%', transform: 'translateX(-50%)', background: 'var(--accent-cyan)', color: '#000', padding: '4px 12px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 700 }}>MOST POPULAR</div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Pro Designer</h3>
            <div style={{ fontSize: '3rem', fontWeight: 700, marginBottom: '20px', color: 'var(--accent-cyan)' }}>$99<span style={{ fontSize: '1rem', color: 'var(--text-secondary)', fontWeight: 400 }}>/mo</span></div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '30px' }}>For professional engineers needing unconstrained workflows.</p>
            <ul style={{ listStyle: 'none', marginBottom: '40px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-cyan)" /> Unlimited Exports</li>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-cyan)" /> Full standards compliance (ASME)</li>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-cyan)" /> Sketch & Image processing</li>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-cyan)" /> Priority generation queue</li>
            </ul>
            <button className="btn btn-primary" style={{ width: '100%' }}>Upgrade to Pro</button>
          </div>

          {/* Enterprise Tier */}
          <div className="glass-panel" style={{ padding: '40px' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Enterprise</h3>
            <div style={{ fontSize: '3rem', fontWeight: 700, marginBottom: '20px' }}>Custom</div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '30px' }}>For large firms requiring custom model training.</p>
            <ul style={{ listStyle: 'none', marginBottom: '40px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-green)" /> Custom Symbol Libraries</li>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-green)" /> Dedicated compute nodes</li>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-green)" /> API access for integrations</li>
              <li style={{ display: 'flex', gap: '10px' }}><Check color="var(--accent-green)" /> SSO and Team Management</li>
            </ul>
            <button className="btn btn-secondary" style={{ width: '100%', borderColor: 'var(--accent-green)', color: 'var(--accent-green)' }}>Contact Sales</button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
