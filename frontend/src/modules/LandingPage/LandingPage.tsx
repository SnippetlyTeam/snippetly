import CodeEditor from '../../components/CodeEditor/CodeEditor';
import MainButton from '../../components/MainButton/MainButton';
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

      <CodeEditor />
      <MainButton content='Start Coding' />
    </main>
  )
}

export default LandingPage;