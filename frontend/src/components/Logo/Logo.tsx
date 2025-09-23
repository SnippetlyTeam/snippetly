import { NavLink } from "react-router-dom";
import styles from './Logo.module.scss';

type Props = { type: 'large' | 'small' }


const Logo: React.FC<Props> = ({ type }) => (
  <NavLink
    to="/"
    className={`
      ${styles.logo} 
      ${type === 'large' ? styles.large : styles.small}
    `}
  >
    Snippetly
  </NavLink>
);

export default Logo;