import { NavLink } from "react-router-dom";
import styles from './Logo.module.scss';

const Logo: React.FC = () => (
  <NavLink to="/" className={styles.logo}>
    Snippetly
  </NavLink>
);

export default Logo;