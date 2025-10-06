import styles from './PublicOnlyRoute.module.scss';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../Loader';

const PublicOnlyRoute = () => {
  const { isAuthenticated, isTokenLoading } = useAuthContext();

  if (isTokenLoading) {
    return (
      <main className={styles.main}>
        <Loader />
      </main>
    );
  }
  if (isAuthenticated) {
    return <Navigate to="/snippets" replace />;
  }

  return <Outlet />;
};

export default PublicOnlyRoute;