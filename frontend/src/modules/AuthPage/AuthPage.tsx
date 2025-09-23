import { Link } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useState } from 'react';
import UncrossedEye from './UncrossedEye';
import CrossedEye from './CrossedEye';

type Props = { formType: 'login' | 'signup' }

const AuthPage: React.FC<Props> = ({ formType }) => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const isSignUp = formType === 'signup';

  return (
    <main className={styles.main}>
      <h2>{isSignUp ? 'Sign Up' : 'Log In'}</h2>

      <form action="#" className={styles.form}>
        <div className={styles.inputs}>
          <div className={styles.inputsItem}>
            <label
              htmlFor="email"
              className={styles.inputsTitle}
            >
              Email
            </label>
            <input
              className={styles.input}
              id="email"
              type="email"
              placeholder="Enter your email"
            />
          </div>
          <div className={styles.inputsItem}>
            <label
              htmlFor="password"
              className={styles.inputsTitle}>
              Password
            </label>
            <div className={styles.container}>
              <input
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="password"
                placeholder={isSignUp ? 'Create a password' : 'Enter your password'}
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
          </div>
        </div>

        <button
          type="submit"
          className={styles.button}
        >{isSignUp ? 'Sign Up' : 'Log In'}</button>

        {isSignUp ? (
          <p className={styles.text}>
            Already have an account? <Link to='/login'>Log In</Link>
          </p>
        ) : (
          <p className={styles.text}>
            Don't have an account? <Link to='/signup'>Sign Up</Link>
          </p>
        )}
      </form>
    </main>
  )
}

export default AuthPage;