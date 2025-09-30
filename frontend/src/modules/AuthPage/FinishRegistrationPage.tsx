import styles from './AuthPage.module.scss';

const FinishRegistrationPage: React.FC = () => {

  return (
    <main className={styles.main}>
      <h2>Finish Registration</h2>

      <form
        noValidate
        action="#"
        className={styles.form}
        onSubmit={(event) => event.preventDefault()}
      >
        <div className={styles.inputs}>
          <div className={styles.inputsItem}>
            <div className={styles.inputsTitle}>
              A confirmation link has been sent to your email address
            </div>
            <div className={styles.container}>
              <div className={styles.inputsDescription}>
                Please click the link in the email to activate your Snippetly account.
                Check your spam folder if you don't see it within a few minutes.
              </div>
            </div>
          </div>
        </div>
      </form>
    </main>
  );
}

export default FinishRegistrationPage;