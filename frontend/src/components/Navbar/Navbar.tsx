import React from 'react';
import styles from './Navbar.module.scss';
import Logo from '../Logo/Logo';

const Navbar: React.FC = () => {
  return (
    <nav className={styles.nav}>
      <Logo />
    </nav>
  );
};

export default Navbar;
