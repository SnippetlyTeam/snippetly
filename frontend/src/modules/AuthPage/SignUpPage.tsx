import { Link } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useState } from 'react';
import UncrossedEye from './UncrossedEye';
import CrossedEye from './CrossedEye';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const SignUpPage: React.FC = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  const signupSchema = z.object({
    username: z.string()
      .min(3)
      .max(40)
      .regex(/^[A-Za-z][A-Za-z0-9_]*$/),
    email: z.email(),
    password: z.string()
      .min(8)
      .regex(/^\S+$/),
    confirmPassword: z.string(),
  }).refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match.',
    path: ['confirmPassword']
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(signupSchema),
  });

  function handleFormSubmit() { }

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
            <label
              htmlFor="username"
              className={styles.inputsTitle}
              id="username-label"
            >
              Username
            </label>
            <input
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
            <label
              htmlFor="email"
              className={styles.inputsTitle}
              id="email-label"
            >
              Email
            </label>
            <input
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
            <label
              htmlFor="password"
              className={styles.inputsTitle}
              id="password-label"
            >
              Password
            </label>
            <div className={styles.container}>
              <input
                {...register('password')}
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="password"
                placeholder={'Create your password'}
                maxLength={30}
                autoComplete="new-password"
                aria-describedby={
                  errors.password
                    ? "password-label password-error"
                    : "password-label"
                }
                aria-invalid={errors.password ? "true" : undefined}
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
            <label
              htmlFor="confirmPassword"
              className={styles.inputsTitle}
              id="confirmPassword-label"
            >
              Confirm password
            </label>
            <div className={styles.container}>
              <input
                {...register('confirmPassword')}
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="confirmPassword"
                placeholder={'Confirm your password'}
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
                type='button'
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
        >Sign Up</button>

        <p className={styles.text}>
          Have an account? <Link to='/sign-in'>Sign In</Link>
        </p>
      </form>
    </main>
  )
}

export default SignUpPage;