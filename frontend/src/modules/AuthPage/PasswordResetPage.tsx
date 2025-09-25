import { Link } from 'react-router-dom';
import styles from './AuthPage.module.scss';

import { useState } from 'react';

const PasswordResetPage: React.FC = () => {
  const [emailInputValue, setEmailInputValue] = useState('');

  const [isEmailError, setIsEmailError] = useState(false);

  function handleEmailInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setEmailInputValue(event.target.value);

    if (isEmailError) {
      setIsEmailError(false);
    }
  }

  function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (emailInputValue.length === 0) {
      setIsEmailError(true);
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
            <label
              htmlFor="usernameOrEmail"
              className={styles.inputsDescription}
            >
              Enter your email address below, and we'll send you a link to reset your password.
            </label>
            <input
              required
              className={styles.input}
              id="usernameOrEmail"
              type="text"
              autoComplete="username"
              placeholder="Enter your email address"
              value={emailInputValue}
              onChange={handleEmailInputChange}
            />

            {isEmailError && (
              <p className={styles.error}>Email is required</p>
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