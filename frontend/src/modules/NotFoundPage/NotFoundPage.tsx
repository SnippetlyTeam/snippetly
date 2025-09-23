import { useNavigate } from 'react-router-dom';
import MainButton from '../../components/MainButton/MainButton';
import styles from './NotFoundPage.module.scss';

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();
  return (
    <main className={styles.main}>
      <h1>404</h1>
      <p className={styles.text}>Page Not Found</p>
      <MainButton 
        content='Go to Homepage' 
        onClick={() => navigate('/', { replace: true })}
      />
    </main>
  )
}

export default NotFoundPage;