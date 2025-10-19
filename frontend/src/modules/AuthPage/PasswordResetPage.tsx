import { Link, useNavigate } from 'react-router-dom';
import styles from './AuthPage.module.scss';

import { useState } from 'react';
import MainButton from '../../components/MainButton/MainButton';
import { resetRequest } from '../../api/authClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useMutation } from '@tanstack/react-query';

const PasswordResetPage: React.FC = () => {
  const [emailInputValue, setEmailInputValue] = useState('');

  const navigate = useNavigate();

  const { setEmail } = useAuthContext();

  const [errorContent, setErrorContent] = useState('');

  const errors = {
    empty: 'Email is required',
    invalid: 'Please enter a valid email address',
    server: 'Something went wrong. Please try again later.'
  }

  const emailRegex = /^[a-zA-Z0-9+._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  function handleEmailInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setEmailInputValue(event.target.value);

    if (errorContent === errors.empty) {
      setErrorContent('');
    }

    if (errorContent === errors.invalid && emailRegex.test(emailInputValue)) {
      setErrorContent('');
    }
  }

  function handleEmailInputBlur() {
    if (!emailRegex.test(emailInputValue)) {
      setErrorContent(errors.invalid);
    }
  }

  const { mutate, isSuccess, isError } = useMutation({
    mutationFn: (email: string) => resetRequest(email),
  })

  function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    let hasError = false;

    if (emailInputValue.length === 0) {
      setErrorContent(errors.empty);
      hasError = true;
    }

    if (!emailRegex.test(emailInputValue) && emailInputValue.length !== 0) {
      setErrorContent(errors.invalid);
      hasError = true;
    }

    if (hasError) return;

    setEmail(emailInputValue);
    mutate(emailInputValue);
  }

  return (
    <main className={styles.main}>
      <h2>Reset Your Password</h2>

      {isError ? (
        <div className={styles.form}>
          {errors.server}

          <MainButton
            content='Go Home'
            onClick={() => { navigate('/') }}
          />
        </div>
      ) : isSuccess ? (
        <div className={styles.form}>
          If an account with that email exists,
          we've sent password reset instructions.
          Please check your inbox.
        </div>
      ) : (
        <form
          noValidate
          action="#"
          className={styles.form}
          onSubmit={handleFormSubmit}
        >
          <div className={styles.inputs}>
            <div className={styles.inputsItem}>
              <p
                className={styles.inputsDescription}
                id="email-instructions"
              >
                Enter your email address below, and we'll send you a link to reset your password.
              </p>
              <input
                required
                className={styles.input}
                id="email"
                type="email"
                autoComplete="username"
                placeholder="Enter your email address"
                value={emailInputValue}
                onChange={handleEmailInputChange}
                onBlur={handleEmailInputBlur}
                aria-label="Email address"
                aria-describedby={
                  errorContent
                    ? "email-instructions email-error-empty"
                    : "email-instructions"
                }
              />

              {errorContent && (
                <p
                  className={styles.error}
                  id="email-error-empty"
                >
                  {errorContent}
                </p>
              )}
            </div>
          </div>

          <button
            type="submit"
            className={styles.button}
          >Send reset link</button>

          <Link to='/sign-in' className={styles.back}>Back to Sign In</Link>
        </form>
      )}
    </main>
  )
}

export default PasswordResetPage;