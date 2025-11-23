import { Link, useLocation, useNavigate } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useEffect, useState } from 'react';
import UncrossedEye from './UncrossedEye';
import CrossedEye from './CrossedEye';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { register as registerRequest } from '../../api/authClient';
import { useMutation } from '@tanstack/react-query';
import { Loader } from '../../components/Loader';
import toast, { type Toast } from 'react-hot-toast';
import CustomToast from '../../components/CustomToast/CustomToast';
import GoogleSignIn from './GoogleSignIn';

type SignUpForm = {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
};

const SignUpPage: React.FC = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [serverEmailError, setServerEmailError] = useState('');
  const [serverUsernameError, setServerUsernameError] = useState('');
  const [serverPasswordError, setServerPasswordError] = useState('');

  const serverErrors = {
    emailTaken: 'This email is taken. Want to log in?',
    usernameTaken: 'This username is taken.',
  };

  const location = useLocation();
  const navigate = useNavigate();

  const { mutate: signUp, isPending } = useMutation({
    mutationFn: ({ username, email, password }:
      { username: string; email: string; password: string }) =>
      registerRequest(username, email, password),
    onSuccess: () => {
      navigate('/activate-account');
    },
    onError: (error: any) => {
      if (error?.response?.data?.detail && typeof error.response.data.detail === 'string') {
        const detail = error.response.data.detail;
        if (detail.includes('username')) {
          setServerUsernameError(serverErrors.usernameTaken);
        }
        if (detail.includes('email')) {
          setServerEmailError(serverErrors.emailTaken);
        }
        if (detail.includes('Password') || detail.includes('password')) {
          setServerPasswordError(detail);
        }
      }
    },
  });

  const signupSchema = z.object({
    username: z.string()
      .min(3)
      .max(40)
      .regex(/^[A-Za-z][A-Za-z0-9_]*$/),
    email: z.email(),
    password: z.string()
      .min(8)
      .max(30)
      .regex(/^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+\-=?&])\S+$/),
    confirmPassword: z.string(),
  }).refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match.',
    path: ['confirmPassword'],
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<SignUpForm>({
    resolver: zodResolver(signupSchema),
  });

  const watchedFields = watch();

  useEffect(() => {
    if (serverEmailError) {
      setServerEmailError('');
    }
  }, [watchedFields.email]);

  useEffect(() => {
    if (serverUsernameError) {
      setServerUsernameError('');
    }
  }, [watchedFields.username]);

  useEffect(() => {
    if (serverPasswordError) {
      setServerPasswordError('');
    }
  }, [watchedFields.password]);

  useEffect(() => {
    if (location.state && (
      location.state.title ||
      location.state.message ||
      location.state.type
    )) {
      const { title = '', message = '', type = 'success' } = location.state || {};

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

  async function handleFormSubmit(form: SignUpForm) {
    signUp({
      username: form.username,
      email: form.email,
      password: form.password,
    });
  }

  function handleSignUpWithGoogle(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();

    window.location.href = 'http://localhost:8000/api/v1/auth/google/url'
  }

  return (
    <main className={styles.main}>
      <h2 id="sign-up-title">Sign Up</h2>
      <form
        noValidate
        action="#"
        className={styles.form}
        onSubmit={handleSubmit(handleFormSubmit)}
        aria-labelledby="sign-up-title"
      >
        <div className={styles.inputs}>
          <div className={styles.inputsItem}>
            <label htmlFor="username" id="username-label">
              Username
            </label>
            <input
              disabled={isPending}
              {...register('username')}
              className={styles.input}
              maxLength={40}
              id="username"
              type="text"
              autoComplete="username"
              placeholder="Enter your username"
              aria-describedby={
                errors.username
                  ? "username-label username-error"
                  : "username-label"
              }
              aria-invalid={errors.username ? "true" : undefined}
            />
            {serverUsernameError && (
              <p className={styles.error}>{serverUsernameError}</p>
            )}
            {errors.username && (
              <p
                className={styles.error}
                id="username-error"
                role="alert"
                aria-live="assertive"
              >
                Username must start with a letter,
                have no spaces, and be 3 - 40 characters.
              </p>
            )}
          </div>
          <div className={styles.inputsItem}>
            <label htmlFor="email" id="email-label">
              Email
            </label>
            <input
              disabled={isPending}
              {...register('email')}
              className={styles.input}
              id="email"
              type="email"
              autoComplete="email"
              placeholder="Enter your email"
              aria-describedby={
                errors.email
                  ? "email-label email-error"
                  : "email-label"
              }
              aria-invalid={errors.email ? "true" : undefined}
            />
            {serverEmailError && (
              <p className={styles.error}>{serverEmailError}</p>
            )}
            {errors.email && (
              <p
                className={styles.error}
                id="email-error"
                role="alert"
                aria-live="assertive"
              >
                This email does not seem valid.
              </p>
            )}
          </div>
          <div className={styles.inputsItem}>
            <label htmlFor="password" id="password-label">
              Password
            </label>
            <div className={styles.container}>
              <input
                disabled={isPending}
                {...register('password')}
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="password"
                placeholder="Create your password"
                maxLength={30}
                autoComplete="new-password"
                aria-describedby={
                  errors.password
                    ? "password-label password-error"
                    : "password-label"
                }
                aria-invalid={errors.password ? "true" : undefined}
              />
              {serverPasswordError && (
                <p className={styles.error}>{serverPasswordError}</p>
              )}
              <button
                className={styles.eye}
                type="button"
                aria-label={isPasswordVisible ? "Hide password" : "Show password"}
                onMouseDown={() => setIsPasswordVisible(true)}
                onMouseUp={() => setIsPasswordVisible(false)}
                onMouseLeave={() => setIsPasswordVisible(false)}
              >
                {isPasswordVisible ? <UncrossedEye /> : <CrossedEye />}
              </button>
            </div>
            {errors.password && (
              <p
                className={styles.error}
                id="password-error"
                role="alert"
                aria-live="assertive"
              >
                Password can’t be blank.
                Password should contain at least one capital letter,
                one number, and one special character.
              </p>
            )}
          </div>
          <div className={styles.inputsItem}>
            <label htmlFor="confirmPassword" id="confirmPassword-label">
              Confirm password
            </label>
            <div className={styles.container}>
              <input
                disabled={isPending}
                {...register('confirmPassword')}
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="confirmPassword"
                placeholder="Confirm your password"
                maxLength={30}
                autoComplete="new-password"
                aria-describedby={
                  errors.confirmPassword
                    ? "confirmPassword-label confirmPassword-error"
                    : "confirmPassword-label"
                }
                aria-invalid={errors.confirmPassword ? "true" : undefined}
              />
              <button
                className={styles.eye}
                type="button"
                aria-label={isPasswordVisible ? "Hide password" : "Show password"}
                onMouseDown={() => setIsPasswordVisible(true)}
                onMouseUp={() => setIsPasswordVisible(false)}
                onMouseLeave={() => setIsPasswordVisible(false)}
              >
                {isPasswordVisible ? <UncrossedEye /> : <CrossedEye />}
              </button>
            </div>
            {errors.confirmPassword && (
              <p
                className={styles.error}
                id="confirmPassword-error"
                role="alert"
                aria-live="assertive"
              >
                {errors.confirmPassword.message}
              </p>
            )}
          </div>
        </div>
        <button
          type="submit"
          className={styles.button}
          disabled={isPending}
        >
          {isPending ? <Loader buttonContent /> : 'Sign Up'}
        </button>

        <GoogleSignIn type='signup' onClick={handleSignUpWithGoogle} />
        <p className={styles.text}>
          Have an account? <Link to="/sign-in">Sign In</Link>
        </p>
      </form>
    </main>
  );
};

export default SignUpPage;