
import { Hexagon } from 'lucide-react';

const Footer = () => {
  return (
    <footer style={{ borderTop: '1px solid var(--glass-border)', padding: '60px 0 20px', background: 'var(--bg-secondary)' }}>
      <div className="container">
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', gap: '40px', marginBottom: '60px' }}>
          <div style={{ maxWidth: '300px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <Hexagon color="var(--accent-cyan)" size={24} />
              <span style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-heading)' }}>Auto<span className="text-gradient-cyan">CHAD</span></span>
            </div>
            <p style={{ color: 'var(--text-secondary)' }}>
              Automated CAD Design Platform. <br/> Turning simple inputs into production-grade CAD drawings using artificial intelligence.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '60px' }}>
            <div>
              <h4 style={{ marginBottom: '20px', color: '#fff' }}>Products</h4>
              <ul style={{ listStyle: 'none', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <li><a href="#" style={{ transition: 'color 0.2s' }} onMouseOver={e => e.currentTarget.style.color = '#fff'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>PharmaCAD</a></li>
                <li><a href="#" style={{ transition: 'color 0.2s' }} onMouseOver={e => e.currentTarget.style.color = '#fff'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>GeoCAD</a></li>
                <li><a href="#" style={{ transition: 'color 0.2s' }} onMouseOver={e => e.currentTarget.style.color = '#fff'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>API Integrations</a></li>
              </ul>
            </div>
            <div>
              <h4 style={{ marginBottom: '20px', color: '#fff' }}>Company</h4>
              <ul style={{ listStyle: 'none', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <li><a href="#" style={{ transition: 'color 0.2s' }} onMouseOver={e => e.currentTarget.style.color = '#fff'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>About Us</a></li>
                <li><a href="#" style={{ transition: 'color 0.2s' }} onMouseOver={e => e.currentTarget.style.color = '#fff'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>Careers</a></li>
                <li><a href="#" style={{ transition: 'color 0.2s' }} onMouseOver={e => e.currentTarget.style.color = '#fff'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.9rem', borderTop: '1px solid var(--glass-border)', paddingTop: '20px' }}>
          &copy; {new Date().getFullYear()} AutoCHAD Platform. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
