import React from 'react';
import styles from './Navbar.module.scss';
import Logo from '../Logo/Logo';
import { NavLink } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav className={styles.nav}>
      <Logo type='large'/>

      <ul className={styles.list}>
        <li className={styles.listItem}>
          <NavLink
            to='/'
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.activeLink : ''}`
            }
          >
            Home
          </NavLink>
        </li>
        <li className={styles.listItem}>
          <NavLink
            to='/snippets'
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.activeLink : ''}`
            }
          >
            Snippets
          </NavLink>
        </li>
        <li className={styles.listItem}>
          <NavLink
            to='/'
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.activeLink : ''}`
            }
          >
            About
          </NavLink>
        </li>
        <li className={styles.listItem}>
          <NavLink
            to='/sign-in'
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.activeLink : ''}`
            }
          >
            Log In
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
