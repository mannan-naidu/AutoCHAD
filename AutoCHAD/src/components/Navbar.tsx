
import { Hexagon, LogIn } from 'lucide-react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      width: '100%',
      zIndex: 1000,
      padding: '20px 0',
      background: 'rgba(10, 10, 15, 0.8)',
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid var(--glass-border)'
    }}>
      <div className="container" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Hexagon color="var(--accent-cyan)" size={32} />
          <span style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            fontFamily: 'var(--font-heading)'
          }}>Auto<span className="text-gradient-cyan">CHAD</span></span>
        </Link>

        {/* Links */}
        <div style={{ display: 'flex', gap: '30px', alignItems: 'center' }}>
          <a href="#features" style={{ color: 'var(--text-secondary)', transition: 'color 0.3s' }} onMouseOver={(e) => e.currentTarget.style.color = '#fff'} onMouseOut={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}>Features</a>
          <a href="#products" style={{ color: 'var(--text-secondary)', transition: 'color 0.3s' }} onMouseOver={(e) => e.currentTarget.style.color = '#fff'} onMouseOut={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}>Products</a>
          <a href="#pricing" style={{ color: 'var(--text-secondary)', transition: 'color 0.3s' }} onMouseOver={(e) => e.currentTarget.style.color = '#fff'} onMouseOut={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}>Pricing</a>
          <button className="btn btn-secondary">
            <LogIn size={18} />
            Login
          </button>
          <button className="btn btn-primary pulse-primary">
            Get Started
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
