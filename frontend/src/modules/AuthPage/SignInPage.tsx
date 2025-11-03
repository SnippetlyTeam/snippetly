import { Link, useLocation, useNavigate } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useEffect, useState } from 'react';
import UncrossedEye from './UncrossedEye';
import CrossedEye from './CrossedEye';
import { useAuthContext } from '../../contexts/AuthContext';
import { login } from '../../api/authClient';
import CustomToast from '../../components/CustomToast/CustomToast';
import toast, { type Toast } from 'react-hot-toast';
import { useMutation } from '@tanstack/react-query';
import { Loader } from '../../components/Loader';
import GoogleSignIn from './GoogleSignIn';

const SignInPage: React.FC = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  const [emailInputValue, setEmailInputValue] = useState('');
  const [passwordInputValue, setPasswordInputValue] = useState('');

  const [emailErrorContent, setEmailErrorContent] = useState('');
  const [passwordErrorContent, setPasswordErrorContent] = useState('');

  const navigate = useNavigate();

  const { setAccessToken } = useAuthContext();

  const errors = {
    emailEmpty: 'Email or Username: can’t be blank',
    passwordEmpty: 'Password: can’t be blank',
    emailNotFound: 'User with such email or username not registered.',
    passwordWrong: 'Entered Invalid password! Check your keyboard layout or Caps Lock. Forgot your password?',
  }

  const { mutate: signIn, isPending } = useMutation({
    mutationFn: async ({ emailOrUsername, password }: { emailOrUsername: string, password: string }) => {
      return login(emailOrUsername, password);
    },
    onSuccess: (response) => {
      setAccessToken(response.data.access_token);

      navigate('/snippets', {
        replace: true,
        state: {
          title: 'Signed In Successfully',
          message: 'You have signed in.',
          type: 'success',
        }
      });
    },
    onError: (error: any) => {
      if (error?.response?.data?.detail && typeof error.response.data.detail === 'string') {
        const detail = error.response.data.detail;
        if (detail.includes('not registered')) {
          setEmailErrorContent(errors.emailNotFound);
        } else if (detail.includes('Invalid password')) {
          setPasswordErrorContent(errors.passwordWrong);
        } else {
          setEmailErrorContent('Sign in failed. Please try again.');
        }
      } else {
        setEmailErrorContent('Sign in failed. Please try again.');
      }
    }
  });

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

    signIn({
      emailOrUsername: emailInputValue,
      password: passwordInputValue,
    });
  }

  function handleSignInWithGoogle(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();

    window.location.href = 'http://localhost:8000/api/v1/auth/google/url'
  }

  const location = useLocation();

  useEffect(() => {
    if (location.state && (
      location.state.title ||
      location.state.message ||
      location.state.type
    )) {
      const { title = '', message = '', type = 'info' } = location.state || {};

      toast.custom((t: Toast) => (
        <CustomToast
          t={t}
          title={title}
          message={message}
          type={type}
        />
      ), {
        duration: 2500,
      });

      navigate(location.pathname, { replace: true, state: null });
    }
  }, [location, navigate]);

  return (
    <main className={styles.main}>
      <h2>Sign In</h2>

      <form
        noValidate
        className={styles.form}
        onSubmit={handleFormSubmit}
        aria-labelledby="sign-in-title"
      >
        <div className={styles.inputs}>
          <div className={styles.inputsItem}>
            <label
              htmlFor="usernameOrEmail"
              id="usernameOrEmail-label"
            >
              Email or username
            </label>
            <input
              required
              disabled={isPending}
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
            <label htmlFor="password" id="password-label">
              Password
            </label>
            <div className={styles.container}>
              <input
                required
                disabled={isPending}
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

            <Link to='/reset-password' id="forgot-password-link">
              Forgot the password?
            </Link>
          </div>
        </div>

        <button
          type="submit"
          className={styles.button}
          aria-label="Sign in to your account"
        >{isPending ? <Loader buttonContent /> : 'Sign In'}</button>

        <GoogleSignIn type='signin' onClick={handleSignInWithGoogle} />

        <p className={styles.text}>
          Need an account? <Link to='/sign-up'>Sign Up</Link>
        </p>
      </form>
    </main>
  )
}

export default SignInPage;