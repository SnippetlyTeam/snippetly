import styles from './AuthPage.module.scss';

type Props = {
  type: 'signup' | 'signin';
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

const GoogleSignIn: React.FC<Props> = ({ type, onClick }) => (
  <button
    onClick={onClick}
    className={styles.google}
    type="button"
  >
    {type === 'signin' ? 'Sign In with Google' : 'Sign Up with Google'}
    <img
      className={styles.googleIcon}
      src="./icons/google.webp"
      alt="Google"
    />
  </button>
);

export default GoogleSignIn;