import { Link } from 'react-router-dom';
import styles from './AuthPage.module.scss';

import { useState } from 'react';

const PasswordResetPage: React.FC = () => {
  const [emailInputValue, setEmailInputValue] = useState('');

  const [isEmptyError, setIsEmptyError] = useState(false);
  const [isValidError, setIsValidError] = useState(false);

  const emailRegex = /^[a-zA-Z0-9+._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  function handleEmailInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setEmailInputValue(event.target.value);

    if (isEmptyError) {
      setIsEmptyError(false);
    }

    if (!isValidError || emailRegex.test(emailInputValue)) {
      setIsValidError(false);
    }
  }

  function handleEmailInputBlur() {
    if (emailInputValue.length === 0) {
      setIsValidError(false);
      return;
    }
    if (!emailRegex.test(emailInputValue)) {
      setIsValidError(true);
    }
  }

  function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (emailInputValue.length === 0) {
      setIsEmptyError(true);
      setIsValidError(false);
    }
  }

  return (
    <main className={styles.main}>
      <h2>Reset Your Password</h2>

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
                isEmptyError
                  ? "email-instructions email-error-empty"
                  : isValidError && !isEmptyError
                  ? "email-instructions email-error-invalid"
                  : "email-instructions"
              }
            />

            {isEmptyError && (
              <p
                className={styles.error}
                id="email-error-empty"
              >
                Email is required
              </p>
            )}

            {isValidError && !isEmptyError && (
              <p
                className={styles.error}
                id="email-error-invalid"
              >
                Please enter a valid email address
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
    </main>
  )
}

export default PasswordResetPage;