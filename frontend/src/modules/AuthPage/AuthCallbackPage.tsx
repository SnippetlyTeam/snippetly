import { useSearchParams, useNavigate } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useEffect, useState } from 'react';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';
import MainButton from '../../components/MainButton/MainButton';

const AuthCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { setAccessToken } = useAuthContext();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      setError('No code provided in callback.');
      return;
    }

    const fetchCallback = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/google/callback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code })
        });

        if (!response.ok) {
          throw new Error('Failed to authenticate with Google.');
        }

        const data = await response.json();

        setAccessToken(data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);

        navigate('/snippets', { replace: true });
      } catch (err: any) {
        setError(err.message || 'An error occurred during authentication.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCallback();
  }, []);

  return (
    <main className={styles.main}>
      {isLoading ? (
        <Loader />
      ) : error ? (
        <div className={styles.form}>
          <p className={styles.text}>{error}</p>

          <MainButton
            content='Go to Sign In'
            onClick={() => navigate('/sign-in')}
          />
        </div>
      ) : (
        <div>Redirecting...</div>
      )}
    </main>
  );
}

export default AuthCallbackPage;