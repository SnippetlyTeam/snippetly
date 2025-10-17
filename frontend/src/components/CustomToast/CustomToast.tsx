import { toast, type Toast } from 'react-hot-toast';
import styles from './CustomToast.module.scss';

type Props = {
  t: Toast;
  title: string;
  message: string;
  type: 'info' | 'success' | 'error'
}

const CustomToast: React.FC<Props> = ({ t, title, message, type }) => (
  <div
    data-enter={styles.visible}
    data-leave={styles.exiting}

    className={`
    ${styles.toast} ${styles[type]}
    ${t.visible ? styles.visible : ''}
  `}
  >
    <button
      onClick={() => toast.remove(t.id)}
      className={styles.button}
    >
      <svg width="14" height="14" viewBox="0 0 18 18" fill="none"
        xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
        <line x1="4.70711" y1="4.29289" x2="13.3137" y2="12.8995" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <line x1="4.29289" y1="12.8995" x2="12.8995" y2="4.29289" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    </button>
    <div className={styles.container}>
      <strong className={styles.title}>{title}</strong>
      <span className={styles.message}>{message}</span>
    </div>
  </div>
);

export default CustomToast;