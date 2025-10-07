import styles from './ProtectedRoute.module.scss';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../Loader';

const ProtectedRoute = () => {
  const { isAuthenticated, isTokenLoading } = useAuthContext();

  if (isTokenLoading) {
    return (
      <main className={styles.main}>
        <Loader />
      </main>
    );
  }

  if (!isAuthenticated) {
    return <Navigate
      to="/sign-in"
      replace
      state={{ 
        title: 'Sign In Required',
        message: `You must be signed in to view this page.\nPlease sign in to continue.`,
        type: 'info'
      }}
    />;
  }

  return <Outlet />;
};

export default ProtectedRoute;