import { Outlet } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';
import styles from './App.module.scss';

const App: React.FC = () => (
  <div className={styles.app}>
    <header>
      <Navbar />
    </header>
    <div className={styles.mainContent}>
      <Outlet />
    </div>
  </div>
);

export default App
