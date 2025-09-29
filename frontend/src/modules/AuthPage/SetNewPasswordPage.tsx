import styles from './AuthPage.module.scss';
import { useState } from 'react';
import UncrossedEye from './UncrossedEye';
import CrossedEye from './CrossedEye';

type Status = 'Weak' | 'Medium' | 'Strong';

const SetNewPasswordPage: React.FC = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isPasswordConfirmVisible, setIsPasswordConfirmVisible] = useState(false);

  const [passwordStatus, setPasswordStatus] = useState<Status>('Weak');

  const [passwordErrorContent, setPasswordErrorContent] = useState('');
  const [passwordConfirmErrorContent, setPasswordConfirmErrorContent] = useState('');

  const [passwordInputValue, setPasswordInputValue] = useState('');
  const [passwordConfirmInputValue, setPasswordConfirmInputValue] = useState('');

  const errorMessages = {
    passwordEmpty: 'New password is required',
    passwordConfirmEmpty: 'Please confirm your new password',
    passwordMismatch: 'Passwords do not match',
    passwordLength: 'Password must be at least 8 characters long',
    passwordIncludeLetters: 'Include both uppercase and lowercase letters',
    passwordIncludeNumber: 'Include at least one number',
    passwordNonPrinting: 'Non-printing symbols are not allowed',
    passwordSpecial: 'Include at least one special character'
  };

  function checkErrors(password: string): string {
    if (!password) return errorMessages.passwordEmpty;
    if (password.length < 8) return errorMessages.passwordLength;
    if (/\s/.test(password)) return errorMessages.passwordNonPrinting;
    if (!/^[\x20-\x7E]+$/.test(password)) return errorMessages.passwordNonPrinting;
    if (!/[^A-Za-z0-9]/.test(password)) return errorMessages.passwordSpecial;
    if (!/[0-9]/.test(password)) return errorMessages.passwordIncludeNumber;
    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password)) return errorMessages.passwordIncludeLetters;
    return '';
  }

  function changePasswordStatus(password: string) {
    let score = 0;

    const regex = {
      has_uppercase: /[A-Z]/,
      has_lowercase: /[a-z]/,
      has_number: /[0-9]/,
      has_special: /[^A-Za-z0-9]/,
    };

    if (password.length >= 8) {
      score += 1;
    }

    if (regex.has_uppercase.test(password)) {
      score += 1;
    }
    if (regex.has_lowercase.test(password)) {
      score += 1;
    }
    if (regex.has_number.test(password)) {
      score += 1;
    }

    if (regex.has_special.test(password)) {
      score += 1;
    }

    if (score <= 2) {
      setPasswordStatus('Weak');
    } else if (score <= 4) {
      setPasswordStatus('Medium');
    } else {
      setPasswordStatus('Strong');
    }
  }

  function handlePasswordInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const newValue = event.target.value;
    setPasswordInputValue(newValue);
    changePasswordStatus(newValue);
    setPasswordErrorContent('');

    if (passwordConfirmInputValue) {
      if (newValue !== passwordConfirmInputValue) {
        setPasswordConfirmErrorContent(errorMessages.passwordMismatch);
      } else {
        setPasswordConfirmErrorContent('');
      }
    }
  }

  function handlePasswordConfirmInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const newValue = event.target.value;
    setPasswordConfirmInputValue(newValue);
    if (!newValue) {
      setPasswordConfirmErrorContent(errorMessages.passwordConfirmEmpty);
    } else if (passwordInputValue !== newValue) {
      setPasswordConfirmErrorContent(errorMessages.passwordMismatch);
    } else {
      setPasswordConfirmErrorContent('');
    }
  }

  function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const passwordError = checkErrors(passwordInputValue);
    setPasswordErrorContent(passwordError);

    if (!passwordConfirmInputValue) {
      setPasswordConfirmErrorContent(errorMessages.passwordConfirmEmpty);
      return;
    }

    if (!passwordError && passwordInputValue !== passwordConfirmInputValue) {
      setPasswordConfirmErrorContent(errorMessages.passwordMismatch);
      return;
    }
  }

  return (
    <main className={styles.main}>
      <h2>Set New Password</h2>

      <form
        noValidate
        action="#"
        className={styles.form}
        onSubmit={handleFormSubmit}
      >
        <div className={styles.inputs}>
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
                className={styles.input}
                type={isPasswordVisible ? 'text' : 'password'}
                id="password"
                placeholder={'Enter new password'}
                maxLength={30}
                autoComplete="new-password"
                value={passwordInputValue}
                onChange={handlePasswordInputChange}
                aria-describedby={
                  passwordErrorContent
                    ? "password-label password-error"
                    : "password-label"
                }
                aria-invalid={passwordErrorContent ? "true" : undefined}
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

            {passwordInputValue && (
              <div className={styles.strength}>
                <div
                  className={`
                    ${styles[`strength-Line-${passwordStatus}`]}
                    ${styles[`strength-Line`]}
                  `}></div>
                <p
                  className={`
                    ${styles['strength-Status']} 
                    ${styles[`strength-Status-${passwordStatus}`]}
                  `}
                >{passwordStatus}</p>
              </div>
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
                className={styles.input}
                type={isPasswordConfirmVisible ? 'text' : 'password'}
                id="confirmPassword"
                placeholder={'Confirm new password'}
                maxLength={30}
                autoComplete="new-password"
                value={passwordConfirmInputValue}
                onChange={handlePasswordConfirmInputChange}
                aria-describedby={
                  passwordConfirmErrorContent
                    ? "confirmPassword-label confirmPassword-error"
                    : "confirmPassword-label"
                }
                aria-invalid={passwordConfirmErrorContent ? "true" : undefined}
              />
              <button
                className={styles.eye}
                type='button'
                aria-label={isPasswordConfirmVisible ? "Hide password" : "Show password"}
                onMouseDown={() => setIsPasswordConfirmVisible(true)}
                onMouseUp={() => setIsPasswordConfirmVisible(false)}
                onMouseLeave={() => setIsPasswordConfirmVisible(false)}
              >
                {isPasswordConfirmVisible ? <UncrossedEye /> : <CrossedEye />}
              </button>
            </div>

            {passwordConfirmErrorContent && (
              <p
                className={styles.error}
                id="confirmPassword-error"
                role="alert"
                aria-live="assertive"
              >
                {passwordConfirmErrorContent}
              </p>
            )}
          </div>
        </div>

        <button
          type="submit"
          className={styles.button}
          aria-label="Reset your password"
        >Reset Password</button>
      </form>
    </main>
  );
};

export default SetNewPasswordPage;