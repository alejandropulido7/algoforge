import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, Database, LogOut, Menu, Activity, BarChart2 } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import styles from '../../styles/layout.module.css';

const Sidebar: React.FC = () => {
  const { user, signOut } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  const toggleSidebar = () => setIsOpen(!isOpen);

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/new', label: 'New Strategy', icon: PlusCircle },
    { to: '/data', label: 'Data Manager', icon: Database },
    { to: '/indicators', label: 'Indicators', icon: BarChart2 },
  ];

  return (
    <>
      <div className={styles.mobileHeader}>
        <div className={styles.logo}>
          <Activity size={20} className="text-cyan inline mr-2" />
          AlgoForge
        </div>
        <button className={styles.hamburger} onClick={toggleSidebar}>
          <Menu size={24} />
        </button>
      </div>

      {isOpen && <div className={styles.sidebarOverlay} onClick={() => setIsOpen(false)} />}

      <aside className={`${styles.sidebar} ${isOpen ? styles.sidebarOpen : ''}`}>
        <div className={styles.sidebarHeader}>
          <div className={styles.logoWrapper}>
            <div className={styles.logoIcon}>
              <Activity size={22} className="text-cyan" />
            </div>
            <span className={styles.logoText}>AlgoForge</span>
          </div>
        </div>

        <nav className={styles.sidebarNav}>
          {navLinks.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`}
                onClick={() => setIsOpen(false)}
              >
                <Icon size={18} className={styles.navIcon} />
                {link.label}
              </NavLink>
            );
          })}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.userInfo}>
            <div className={styles.userAvatar}>
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className={styles.userEmail}>{user?.email}</span>
          </div>
          <button className={styles.logoutBtn} onClick={() => signOut()}>
            <LogOut size={16} className="mr-1" />
            Logout
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
