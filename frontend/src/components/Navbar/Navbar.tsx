import React from 'react';
import styles from './Navbar.module.scss';
import Logo from '../Logo/Logo';
import { NavLink } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { isAuthenticated } = useAuthContext();

  return (
    <nav className={styles.nav}>
      <Logo type='large' />

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
            Favourites
          </NavLink>
        </li>
        {isAuthenticated ? (
          <li className={styles.listItem}>
            <NavLink
              to='/profile'
              className={({ isActive }) =>
                `${styles.link} ${isActive ? styles.activeLink : ''}`
              }
            >
              Profile
            </NavLink>
          </li>
        ) : (
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
        )}
      </ul>
    </nav >
  );
};

export default Navbar;
