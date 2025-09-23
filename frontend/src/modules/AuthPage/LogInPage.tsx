import styles from './AuthPage.module.scss';

const LogInPage = () => (
  <main className={styles.main}>
    <h2>Log In</h2>

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
          <input
            className={styles.input}
            type="password"
            id="password"
            placeholder="Enter your password"
          />
        </div>
      </div>

      <button type="submit">Log In</button>

      <p>Don't have an account?</p>

    </form>
  </main>
)

export default LogInPage;