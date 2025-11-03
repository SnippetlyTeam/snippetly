import { useSearchParams, useNavigate } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useEffect, useState } from 'react';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';
import MainButton from '../../components/MainButton/MainButton';
import axios from 'axios';
import { flushSync } from 'react-dom';

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
        const response = await axios.post('http://localhost:8000/api/v1/auth/google/callback',
          { code },
          { headers: { 'Content-Type': 'application/json' } }
        );
        flushSync(() => setAccessToken(response.data.access_token));
        navigate('/snippets', {
          replace: true,
          state: {
            title: 'Signed In Successfully',
            message: 'You have signed in with Google.',
            type: 'success',
          }
        });
      } catch (err: any) {
        setError(
          err.response?.data?.message ||
          err.message ||
          'An error occurred during authentication.'
        );
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