import { Navigate, useParams } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useEffect, useState } from 'react';
import { activate } from '../../api/authClient';
import { Loader } from '../../components/Loader';

const FinishRegistrationTokenPage = () => {
  const { token } = useParams();

  const [isLoading, setIsLoading] = useState(true);
  const [isValid, setIsValid] = useState<null | boolean>(null);

  useEffect(() => {
    if (!token) {
      setIsValid(false);
      setIsLoading(false);
      return;
    }

    activate(token)
      .then(response => {
        if (response && response.status === 200) {
          setIsValid(true);
        } else {
          setIsValid(false);
        }
      })
      .catch(() => {
        setIsValid(false);
      })
      .finally(() => setIsLoading(false));
  }, [token]);

  return (
    <main className={styles.main}>
      {isLoading ? (
        <Loader />
      ) : isValid === true ? (
        <Navigate
          to='/sign-in'
          state={{
            title: 'Registration Complete',
            message: 'Your account has been successfully activated.',
            type: 'success'
          }}
        />
      ) : (
        <Navigate
          to='/sign-up'
          state={{
            title: 'Activation Failed',
            message: 'The activation link is invalid or has expired. Please sign up again.',
            type: 'error'
          }}
        />
      )}
    </main>
  );
}

export default FinishRegistrationTokenPage;