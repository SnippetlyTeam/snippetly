import type { Toast } from 'react-hot-toast';
import styles from './CustomToast.module.scss';

type Props = {
  t: Toast;
  title: string;
  message: string;
  type: 'info' | 'success' | 'error'
}

const CustomToast: React.FC<Props> = ({ t, title, message, type }) => (
  <div className={`
    ${styles.toast} ${styles[type]}
    ${t.visible ? styles.visible : ''}
  `}>
    <strong className={styles.title}>{title}</strong>
    <span className={styles.message}>{message}</span>
  </div>
);

export default CustomToast;