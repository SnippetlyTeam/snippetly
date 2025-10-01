import { Link, useNavigate } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useState } from 'react';
import UncrossedEye from './UncrossedEye';
import CrossedEye from './CrossedEye';

const SignInPage: React.FC = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  const [emailInputValue, setEmailInputValue] = useState('');
  const [passwordInputValue, setPasswordInputValue] = useState('');

  const [emailErrorContent, setEmailErrorContent] = useState('');
  const [passwordErrorContent, setPasswordErrorContent] = useState('');

  const navigate = useNavigate();

  const errors = {
    emailEmpty: 'Email or Username: can’t be blank',
    passwordEmpty: 'Password: can’t be blank',
    emailNotFound: 'User with such email or username not registered.',
    passwordWrong: 'Entered Invalid password! Check your keyboard layout or Caps Lock. Forgot your password?',
  }

  function handleEmailInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setEmailInputValue(event.target.value);

    if (emailErrorContent) {
      setEmailErrorContent('');
    }
  }

  function handlePasswordInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setPasswordInputValue(event.target.value);

    if (passwordErrorContent) {
      setPasswordErrorContent('');
    }
  }

  function validatePassword() {
    if (!passwordInputValue.trim()) {
      setPasswordErrorContent(errors.passwordEmpty);
      return false;
    }

    const hasCapital = /[A-Z]/.test(passwordInputValue);
    const hasNumber = /[0-9]/.test(passwordInputValue);
    const hasSpecial = /[^A-Za-z0-9]/.test(passwordInputValue);

    if (!hasCapital || !hasNumber || !hasSpecial) {
      setPasswordErrorContent(errors.passwordWrong);
      return false;
    }

    setPasswordErrorContent('');
    return true;
  }

  function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    let hasError = false;

    if (!emailInputValue.trim()) {
      setEmailErrorContent(errors.emailEmpty);
      hasError = true;
    }

    if (!validatePassword()) {
      hasError = true;
    }

    if (hasError) return;

    fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        login: emailInputValue,
        password: passwordInputValue
      })
    })
      .then(response => {
        switch (response.status) {
          case 200:
            navigate('/');
            break;
          case 403:
            setPasswordErrorContent(errors.passwordWrong);
            break;
          case 404:
            setEmailErrorContent(errors.emailNotFound);
            break;
        }
      })
  }

  function handleSignInWithGoogle(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();

    window.location.href = 'http://localhost:8000/api/v1/auth/google/url'
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
                emailErrorContent
                  ? "usernameOrEmail-label usernameOrEmail-error"
                  : "usernameOrEmail-label"
              }
              aria-invalid={emailErrorContent ? "true" : undefined}
            />

            {emailErrorContent && (
              <p
                className={styles.error}
                id="usernameOrEmail-error"
                role="alert"
                aria-live="assertive"
              >
                {emailErrorContent}
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
                  passwordErrorContent
                    ? "password-label password-error"
                    : "password-label"
                }
                aria-invalid={passwordErrorContent ? "true" : undefined}
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

            {passwordErrorContent && (
              <p
                className={styles.error}
                id="password-error"
                role="alert"
                aria-live="assertive"
              >
                {passwordErrorContent}
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

        <button
          onClick={handleSignInWithGoogle}
          className={styles.google}
        >
          Sign In with Google <img className={styles.googleIcon} src='./icons/google.webp' alt='Google' />
        </button>

        <p className={styles.text}>
          Need an account? <Link to='/sign-up'>Sign Up</Link>
        </p>
      </form>
    </main>
  )
}

export default SignInPage;