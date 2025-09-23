import styles from './LandingPage.module.scss';

const LandingPage: React.FC = () => {
  return (
    <main className={styles.main}>
      <div className={styles.description}>
        <h1 className={styles.title}>Store and Share Your Code Snippets.</h1>
        <p className={styles.text}>
          Save your code snippets, share them with other
          developers, and discover new solutions for your
          projects.
        </p>
      </div>

      <button className={`${styles.button} buttonText`}>Start Coding</button>

      <div className={styles.redactor}>
        
      </div>
    </main>
  )
}

export default LandingPage;