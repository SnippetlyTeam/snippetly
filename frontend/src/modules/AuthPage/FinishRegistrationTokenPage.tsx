import { useNavigate, useParams } from 'react-router-dom';
import MainButton from '../../components/MainButton/MainButton';
import styles from './AuthPage.module.scss';
import { useEffect, useState } from 'react';

const FinishRegistrationTokenPage = () => {
  const navigate = useNavigate();
  const { token } = useParams();

  const [isLoading, setIsLoading] = useState(false);
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    setIsLoading(true);

    fetch('http://localhost:8000/api/v1/auth/activate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        activation_token: token
      })
    })
      .then(response => {
        if (response.status === 200) {
          setIsValid(true);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <main className={styles.main}>
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <>
          {isValid ? <h2 className={styles.success}>Registration Complete</h2> : <h2 className={`${styles.errorTitle} ${styles.error}`}>Registration Error</h2>}

          <div
            className={styles.form}
          >
            <div className={styles.inputs}>
              <div className={styles.inputsItem}>
                {isValid ? (
                  <div className={styles.inputsDescription}>
                    Your account is now active. You can start creating and sharing snippets.
                  </div>
                ) : (
                  <div className={styles.inputsDescription}>
                    Activation failed. The activation link may be invalid or expired. Please try again or contact support.
                  </div>
                )}
              </div>
            </div>

            <MainButton
              content={isValid ? 'Go to Sign In' : 'Go to Sign Up'}
              onClick={() => { navigate(`/sign-${isValid ? 'In' : 'Up'}`) }}
            />
          </div>
        </>
      )}
    </main>
  )
}

export default FinishRegistrationTokenPage;