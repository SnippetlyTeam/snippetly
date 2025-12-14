import styles from './Loader.module.scss';

type Props = {
  buttonContent?: boolean
}

export const Loader: React.FC<Props> = ({ buttonContent }) => (
  <div className={styles.loader}>
    <div
      className={`
        ${styles.loaderContent} 
        ${buttonContent ? styles.buttonContent : ''}
      `}
    />
  </div>
);
