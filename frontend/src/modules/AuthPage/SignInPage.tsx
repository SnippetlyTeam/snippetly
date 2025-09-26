import { Link } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useState } from 'react';
import UncrossedEye from './UncrossedEye';
import CrossedEye from './CrossedEye';

const SignInPage: React.FC = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  
  const [emailInputValue, setEmailInputValue] = useState('');
  const [passwordInputValue, setPasswordInputValue] = useState('');

  const [isEmailError, setIsEmailError] = useState(false);
  const [isPasswordError, setIsPasswordError] = useState(false);

  function handleEmailInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setEmailInputValue(event.target.value);

    if (isEmailError) {
      setIsEmailError(false);
    }
  }

  function handlePasswordInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setPasswordInputValue(event.target.value);

    if (isPasswordError) {
      setIsPasswordError(false);
    }
  }

  function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!emailInputValue.trim()) {
      setIsEmailError(true);
    }

    if (!passwordInputValue.trim()) {
      setIsPasswordError(true);
    }
  }

  return (
    <main className={styles.main}>
      <h2>Sign In</h2>

      <form
        noValidate
        action="#"
        className={styles.form}
        onSubmit={handleFormSubmit}
        aria-labelledby="sign-in-title"
      >
        <div className={styles.inputs}>
          <div className={styles.inputsItem}>
            <label
              htmlFor="usernameOrEmail"
              className={styles.inputsTitle}
              id="usernameOrEmail-label"
            >
              Email or username
            </label>
            <input
              required
              value={emailInputValue}
              className={styles.input}
              id="usernameOrEmail"
              type="text"
              autoComplete="username"
              placeholder="Enter your username or email"
              onChange={handleEmailInputChange}
              aria-describedby={
                isEmailError
                  ? "usernameOrEmail-label usernameOrEmail-error"
                  : "usernameOrEmail-label"
              }
              aria-invalid={isEmailError ? "true" : undefined}
            />

            {isEmailError && (
              <p
                className={styles.error}
                id="usernameOrEmail-error"
                role="alert"
                aria-live="assertive"
              >
                Email or Username: can’t be blank
              </p>
            )}
          </div>
          <div className={styles.inputsItem}>
            <label
              htmlFor="password"
              className={styles.inputsTitle}
              id="password-label"
            >
              Password
            </label>
            <div className={styles.container}>
              <input
                required
                value={passwordInputValue}
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="password"
                placeholder={'Enter your password'}
                onChange={handlePasswordInputChange}
                aria-describedby={
                  isPasswordError
                    ? "password-label password-error"
                    : "password-label"
                }
                aria-invalid={isPasswordError ? "true" : undefined}
                autoComplete="current-password"
              />
              <button
                className={styles.eye}
                type='button'
                aria-label={isPasswordVisible ? "Hide password" : "Show password"}
                onMouseDown={() => setIsPasswordVisible(true)}
                onMouseUp={() => setIsPasswordVisible(false)}
                onMouseLeave={() => setIsPasswordVisible(false)}
              >
                {isPasswordVisible ? <UncrossedEye /> : <CrossedEye />}
              </button>
            </div>

            {isPasswordError && (
              <p
                className={styles.error}
                id="password-error"
                role="alert"
                aria-live="assertive"
              >
                Password: can’t be blank
              </p>
            )}

            <Link to='/password-reset' id="forgot-password-link">
              Forgot the password?
            </Link>
          </div>
        </div>

        <button
          type="submit"
          className={styles.button}
          aria-label="Sign in to your account"
        >Sign In</button>

        <p className={styles.text}>
          Need an account? <Link to='/sign-up'>Sign Up</Link>
        </p>
      </form>
    </main>
  )
}

export default SignInPage;