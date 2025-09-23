import styles from './AuthPage.module.scss';

const SignUpPage = () => (
  <main className={styles.main}>
    <h2>Sign Up</h2>

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
            placeholder="Create a password"
          />
        </div>
      </div>

      <button type="submit">Sign Up</button>

      <p>Already have an account?</p>

    </form>
  </main>
)

export default SignUpPage;