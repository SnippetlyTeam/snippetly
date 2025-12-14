import { useState } from 'react';
import styles from './ChangePasswordPage.module.scss';
import UncrossedEye from '../AuthPage/UncrossedEye';
import CrossedEye from '../AuthPage/CrossedEye';
import { changePassword } from '../../api/authClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useMutation } from '@tanstack/react-query';
import { Loader } from '../../components/Loader';
import toast, { type Toast } from 'react-hot-toast';
import CustomToast from '../../components/CustomToast/CustomToast';
import { AxiosError } from 'axios';
import { useNavigate } from 'react-router-dom';

type Status = 'Weak' | 'Medium' | 'Strong';

const ChangePasswordPage = () => {
  const [isPasswordOldVisible, setIsPasswordOldVisible] = useState(false);
  const [isPasswordNewVisible, setIsPasswordNewVisible] = useState(false);
  const [isPasswordConfirmVisible, setIsPasswordConfirmVisible] = useState(false);

  const [passwordStatus, setPasswordStatus] = useState<Status>('Weak');

  const [oldPasswordErrorContent, setOldPasswordErrorContent] = useState('');
  const [newPasswordErrorContent, setNewPasswordErrorContent] = useState('');
  const [confirmPasswordErrorContent, setConfirmPasswordErrorContent] = useState('');

  const [oldPasswordInputValue, setOldPasswordInputValue] = useState('');
  const [newPasswordInputValue, setNewPasswordInputValue] = useState('');
  const [confirmPasswordInputValue, setConfirmPasswordInputValue] = useState('');

  const { accessToken } = useAuthContext();
  const navigate = useNavigate();

  const errorMessages = {
    oldPasswordEmpty: 'Old password is required',
    passwordEmpty: 'New password is required',
    passwordConfirmEmpty: 'Please confirm your new password',
    passwordMismatch: 'Passwords do not match',
    passwordSameAsOld: 'New password must be different from old password',
    passwordLength: 'Password must be at least 8 characters long',
    passwordIncludeLetters: 'Include both uppercase and lowercase letters',
    passwordIncludeNumber: 'Include at least one number',
    passwordNonPrinting: 'Non-printing symbols are not allowed',
    passwordSpecial: 'Include at least one special character'
  };

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

  function handleOldPasswordInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const value = event.target.value;
    setOldPasswordInputValue(value);

    setOldPasswordErrorContent(!value ? errorMessages.oldPasswordEmpty : '');

    if (newPasswordInputValue && value === newPasswordInputValue) {
      setNewPasswordErrorContent(errorMessages.passwordSameAsOld);
    } else if (newPasswordErrorContent === errorMessages.passwordSameAsOld) {
      if (!(newPasswordErrorContent === errorMessages.passwordLength && newPasswordInputValue.length < 8)) {
        setNewPasswordErrorContent('');
      }
    }
  }

  function checkNewPasswordErrors(password: string): string {
    if (!password) return errorMessages.passwordEmpty;
    if (password.length < 8) return errorMessages.passwordLength;
    if (/\s/.test(password)) return errorMessages.passwordNonPrinting;
    if (!/^[\x20-\x7E]+$/.test(password)) return errorMessages.passwordNonPrinting;
    if (!/[^A-Za-z0-9]/.test(password)) return errorMessages.passwordSpecial;
    if (!/[0-9]/.test(password)) return errorMessages.passwordIncludeNumber;
    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password)) return errorMessages.passwordIncludeLetters;
    return '';
  }

  function handleNewPasswordInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const newValue = event.target.value;
    setNewPasswordInputValue(newValue);
    changePasswordStatus(newValue);

    setNewPasswordErrorContent('');

    if (oldPasswordInputValue && newValue === oldPasswordInputValue) {
      setNewPasswordErrorContent(errorMessages.passwordSameAsOld);
    }

    if (confirmPasswordInputValue) {
      if (newValue !== confirmPasswordInputValue) {
        setConfirmPasswordErrorContent(errorMessages.passwordMismatch);
      } else {
        setConfirmPasswordErrorContent('');
      }
    }
  }

  function handleConfirmPasswordInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const newValue = event.target.value;
    setConfirmPasswordInputValue(newValue);
    if (!newValue) {
      setConfirmPasswordErrorContent(errorMessages.passwordConfirmEmpty);
    } else if (newPasswordInputValue !== newValue) {
      setConfirmPasswordErrorContent(errorMessages.passwordMismatch);
    } else {
      setConfirmPasswordErrorContent('');
    }
  }

  const { mutate, isPending } = useMutation({
    mutationFn: () => changePassword(oldPasswordInputValue, newPasswordInputValue, accessToken),
    onSuccess: () => navigate('/profile', {
      state: {
        title: 'Password Changed',
        message: 'Your password has been successfully updated',
        type: 'success',
      }
    }),
    onError: (error: AxiosError<{ detail: string | { msg?: string; message?: string }[] | { msg?: string; message?: string } }>) => {
      console.log(error)

      let errorMessage = "An unexpected problem occurred while changing your password.";

      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          const first = detail[0];
          if (typeof first === 'string') {
            errorMessage = first;
          } else if (typeof first === 'object' && (first?.msg || first?.message)) {
            errorMessage = first.msg || first.message || errorMessage;
          }
        } else if (typeof detail === 'object' && (detail?.msg || detail?.message)) {
          errorMessage = detail.msg || detail.message || errorMessage;
        }
      }

      toast.custom((t: Toast) => (
        <CustomToast
          t={t}
          title={"Password Change Error"}
          message={errorMessage}
          type={'error'}
        />
      ), {
        duration: 2500,
      });
    },
  })

  function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (oldPasswordInputValue && oldPasswordInputValue.length < 8) {
      setOldPasswordErrorContent(errorMessages.passwordLength);
      return;
    }

    const newPasswordError = checkNewPasswordErrors(newPasswordInputValue);
    if (newPasswordError) {
      setNewPasswordErrorContent(newPasswordError);
      return;
    }

    if (oldPasswordInputValue === newPasswordInputValue) {
      setNewPasswordErrorContent(errorMessages.passwordSameAsOld);
      return;
    }

    if (!confirmPasswordInputValue) {
      setConfirmPasswordErrorContent(errorMessages.passwordConfirmEmpty);
      return;
    }
    if (newPasswordInputValue !== confirmPasswordInputValue) {
      setConfirmPasswordErrorContent(errorMessages.passwordMismatch);
      return;
    }

    if (oldPasswordErrorContent || newPasswordErrorContent || confirmPasswordErrorContent) {
      return;
    }

    if (passwordStatus !== 'Strong') {
      toast.custom((t: Toast) => (
        <CustomToast
          t={t}
          title={"Weak Password"}
          message={"Please choose a stronger password"}
          type={'error'}
        />
      ), {
        duration: 2500,
      });
      return;
    }

    mutate();
  }

  return (
    <main className={styles.main}>
      <h2 id="change-password-title">Change password</h2>
      <form
        onSubmit={handleFormSubmit}
        className={styles.form}
        aria-labelledby="change-password-title"
      >
        <div className={styles.formItem}>
          <label htmlFor="old-password" id="old-password-label">
            Old password
          </label>
          <div className={styles.container}>
            <input
              className={styles.input}
              type={isPasswordOldVisible ? 'text' : 'password'}
              id="old-password"
              name="old-password"
              placeholder="Enter your current password"
              autoComplete="current-password"
              value={oldPasswordInputValue}
              onChange={handleOldPasswordInputChange}
              aria-describedby={
                oldPasswordErrorContent
                  ? "old-password-label old-password-error"
                  : "old-password-label"
              }
              aria-invalid={oldPasswordErrorContent ? "true" : undefined}
            />
            <button
              className={styles.eye}
              type='button'
              aria-label={isPasswordOldVisible ? "Hide password" : "Show password"}
              onMouseDown={() => setIsPasswordOldVisible(true)}
              onMouseUp={() => setIsPasswordOldVisible(false)}
              onMouseLeave={() => setIsPasswordOldVisible(false)}
            >
              {isPasswordOldVisible ? <UncrossedEye /> : <CrossedEye />}
            </button>
          </div>

          {oldPasswordErrorContent && (
            <p
              className={styles.error}
              id="old-password-error"
              role="alert"
              aria-live="assertive"
            >
              {oldPasswordErrorContent}
            </p>
          )}
        </div>
        <div className={styles.formItem}>
          <label htmlFor="new-password" id="new-password-label">
            New password
          </label>
          <div className={styles.container}>
            <input
              className={styles.input}
              type={isPasswordNewVisible ? 'text' : 'password'}
              id="new-password"
              name="new-password"
              placeholder="Enter your new password"
              maxLength={30}
              autoComplete="new-password"
              value={newPasswordInputValue}
              onChange={handleNewPasswordInputChange}
              aria-describedby={
                newPasswordErrorContent
                  ? "new-password-label new-password-error"
                  : "new-password-label"
              }
              aria-invalid={newPasswordErrorContent ? "true" : undefined}
            />
            <button
              className={styles.eye}
              type='button'
              aria-label={isPasswordNewVisible ? "Hide password" : "Show password"}
              onMouseDown={() => setIsPasswordNewVisible(true)}
              onMouseUp={() => setIsPasswordNewVisible(false)}
              onMouseLeave={() => setIsPasswordNewVisible(false)}
            >
              {isPasswordNewVisible ? <UncrossedEye /> : <CrossedEye />}
            </button>
          </div>

          {newPasswordErrorContent && (
            <p
              className={styles.error}
              id="new-password-error"
              role="alert"
              aria-live="assertive"
            >
              {newPasswordErrorContent}
            </p>
          )}

          {newPasswordInputValue && (
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
        <div className={styles.formItem}>
          <label htmlFor="confirm-new-password" id="confirm-password-label">
            Confirm new password
          </label>
          <div className={styles.container}>
            <input
              className={styles.input}
              type={isPasswordConfirmVisible ? 'text' : 'password'}
              id="confirm-new-password"
              name="confirm-new-password"
              placeholder="Re-enter your new password"
              maxLength={30}
              autoComplete="new-password"
              value={confirmPasswordInputValue}
              onChange={handleConfirmPasswordInputChange}
              aria-describedby={
                confirmPasswordErrorContent
                  ? "confirm-password-label confirm-password-error"
                  : "confirm-password-label"
              }
              aria-invalid={confirmPasswordErrorContent ? "true" : undefined}
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

          {confirmPasswordErrorContent && (
            <p
              className={styles.error}
              id="confirm-password-error"
              role="alert"
              aria-live="assertive"
            >
              {confirmPasswordErrorContent}
            </p>
          )}
        </div>
        <button
          type="submit"
          className={styles.button}
          aria-label="Change password"
        >
          {isPending ? <Loader buttonContent /> : 'Change Password'}
        </button>
      </form>
    </main>
  );
}

export default ChangePasswordPage;