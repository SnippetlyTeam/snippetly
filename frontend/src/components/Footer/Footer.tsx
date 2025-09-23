import Logo from '../Logo/Logo';
import styles from './Footer.module.scss';

const Footer: React.FC = () => (
  <footer className={styles.footer}>
    <div className={styles.footerContent}>
      <Logo type='small' />

      <p>
        Your go-to platform for storing, sharing, and discovering code snippets.<br />
        Simplify your development workflow.
      </p>
    </div>
  </footer>
)

export default Footer;