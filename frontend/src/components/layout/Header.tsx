import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import styles from '../../styles/layout.module.css';

const Header: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  const getPageTitle = () => {
    if (pathnames.length === 0) return 'Dashboard';
    if (pathnames[0] === 'new') return 'New Strategy';
    if (pathnames[0] === 'data') return 'Data Manager';
    if (pathnames[0] === 'jobs') return 'Job Details';
    return pathnames[0].charAt(0).toUpperCase() + pathnames[0].slice(1);
  };

  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <h1 className={styles.pageTitle}>{getPageTitle()}</h1>
        <div className={styles.breadcrumbs}>
          <Link to="/" className={styles.breadcrumbLink}>Home</Link>
          {pathnames.length > 0 && <span className={styles.breadcrumbSeparator}>/</span>}
          {pathnames.map((name, index) => {
            const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
            const isLast = index === pathnames.length - 1;
            return (
              <React.Fragment key={name}>
                {isLast ? (
                  <span className={styles.breadcrumbActive}>{name}</span>
                ) : (
                  <Link to={routeTo} className={styles.breadcrumbLink}>{name}</Link>
                )}
                {!isLast && <span className={styles.breadcrumbSeparator}>/</span>}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </header>
  );
};

export default Header;
