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
      <h2>Sign Up</h2>

      <form
        noValidate
        action="#"
        className={styles.form}
        onSubmit={handleSubmit(handleFormSubmit)}
      >
        <div className={styles.inputs}>
          <div className={styles.inputsItem}>
            <label
              htmlFor="usernameOrEmail"
              className={styles.inputsTitle}
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
            />

            {errors.username && (
              <p className={styles.error}>
                Username must start with a letter,
                have no spaces, and be 3 - 40 characters.
              </p>
            )}
          </div>
          <div className={styles.inputsItem}>
            <label
              htmlFor="usernameOrEmail"
              className={styles.inputsTitle}
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
            />

            {errors.email && (
              <p className={styles.error}>This email does not seem valid.</p>
            )}
          </div>
          <div className={styles.inputsItem}>
            <label
              htmlFor="password"
              className={styles.inputsTitle}>
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
              />
              <button
                className={styles.eye}
                type='button'
                onMouseDown={() => setIsPasswordVisible(true)}
                onMouseUp={() => setIsPasswordVisible(false)}
              >
                {isPasswordVisible ? <UncrossedEye /> : <CrossedEye />}
              </button>
            </div>

            {errors.password && (
              <p className={styles.error}>
                Password can’t be blank.
                Password should contain at least one capital letter,
                one number, and one special character.
              </p>
            )}
          </div>
          <div className={styles.inputsItem}>
            <label
              htmlFor="password"
              className={styles.inputsTitle}>
              Confirm password
            </label>
            <div className={styles.container}>
              <input
                {...register('confirmPassword')}
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="password"
                placeholder={'Confirm your password'}
                maxLength={30}
                autoComplete="new-password"
              />
              <button
                className={styles.eye}
                type='button'
                onMouseDown={() => setIsPasswordVisible(true)}
                onMouseUp={() => setIsPasswordVisible(false)}
              >
                {isPasswordVisible ? <UncrossedEye /> : <CrossedEye />}
              </button>
            </div>

            {errors.confirmPassword && <p className={styles.error}>{errors.confirmPassword.message}</p>}
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