import { Link } from 'react-router-dom';
import styles from './AuthPage.module.scss';
import { useState } from 'react';
import UncrossedEye from './UncrossedEye';
import CrossedEye from './CrossedEye';


const SignUpPage: React.FC = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  const [usernameInputValue, setUsernameInputValue] = useState('');
  const [emailInputValue, setEmailInputValue] = useState('');

  const [passwordInputValue, setPasswordInputValue] = useState('');
  const [confirmPasswordInputValue, setConfirmPasswordInputValue] = useState('');

  const [isUsernameError, setIsUsernameError] = useState(false);
  const [isEmailError, setIsEmailError] = useState(false);
  const [isPasswordError, setIsPasswordError] = useState(false);
  const [isPasswordMatchError, setIsPasswordMatchError] = useState(false);

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

  function handleConfirmPasswordInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setConfirmPasswordInputValue(event.target.value);

    if (isPasswordMatchError) {
      setIsPasswordMatchError(false);
    }
  }

  function handleUsernameInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setUsernameInputValue(event.target.value);

    if (isUsernameError) {
      setIsUsernameError(false);
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

    if (
      !usernameInputValue.trim() ||
      !/^[A-Za-z]/.test(usernameInputValue.trim()) ||
      usernameInputValue.trim().includes(' ') ||
      usernameInputValue.trim().length < 3
    ) {
      setIsUsernameError(true);
    }

    if (passwordInputValue.trim() !== confirmPasswordInputValue) {
      setIsPasswordMatchError(true);
    }
  }

  return (
    <main className={styles.main}>
      <h2>Sign Up</h2>

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
              className={styles.inputsTitle}
            >
              Username
            </label>
            <input
              required
              minLength={3}
              maxLength={40}
              value={usernameInputValue}
              className={styles.input}
              id="usernameOrEmail"
              type="text"
              autoComplete="username"
              placeholder="Enter your username"
              onChange={handleUsernameInputChange}
            />

            {isUsernameError && (
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
              required
              value={emailInputValue}
              className={styles.input}
              id="usernameOrEmail"
              type="email"
              autoComplete="username"
              placeholder="Enter your email"
              onChange={handleEmailInputChange}
            />

            {isEmailError && (
              <p className={styles.error}>Email: can’t be blank</p>
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
                required
                value={passwordInputValue}
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="password"
                placeholder={'Create your password'}
                onChange={handlePasswordInputChange}
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

            {isPasswordError && (
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
                required
                value={confirmPasswordInputValue}
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="password"
                placeholder={'Confirm your password'}
                onChange={handleConfirmPasswordInputChange}
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

            {isPasswordMatchError && <p className={styles.error}>Passwords do not match.</p>}
          </div>
        </div>

        <button
          type="submit"
          className={styles.button}
        >Sign Up</button>


        <p className={styles.text}>
          Have an account? <Link to='/signin'>Sign In</Link>
        </p>
      </form>
    </main>
  )
}

export default SignUpPage;