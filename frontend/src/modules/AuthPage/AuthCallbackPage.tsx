import { useNavigate, useSearchParams } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useEffect, useState } from 'react';
import MainButton from '../../components/MainButton/MainButton';
import { useAppDispatch } from '../../contexts/AppContext';

const AuthCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [isSuccess, setIsSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { setIsAuthorized } = useAppDispatch();

  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) return;

    setIsLoading(true);

    fetch('http://localhost:8000/api/v1/auth/google/callback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    })
      .then(() => {
        setIsSuccess(true);
        setIsAuthorized(true);
      })
      .catch(() => setIsSuccess(false))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <main className={styles.main}>
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <>
          {isSuccess ? <h2 className={styles.success}>Google Sign In Complete</h2> : <h2 className={`${styles.errorTitle} ${styles.error}`}>Google Sign In Error</h2>}

          <div
            className={styles.form}
          >
            <div className={styles.inputs}>
              <div className={styles.inputsItem}>
                {isSuccess ? (
                  <div className={styles.inputsDescription}>
                    You have successfully signed in with Google. You can now start creating and sharing snippets.
                  </div>
                ) : (
                  <div className={styles.inputsDescription}>
                    Google sign in failed. The sign in link may be invalid or expired. Please try again or contact support.
                  </div>
                )}
              </div>
            </div>

            <MainButton
              content={isSuccess ? 'Start Coding' : 'Try Again'}
              onClick={() => { navigate(isSuccess ? '/' : '/sign-in') }}
            />
          </div>
        </>
      )}
    </main>
  )
}

export default AuthCallbackPage;