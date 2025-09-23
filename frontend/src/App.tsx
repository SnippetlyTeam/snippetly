import { Outlet } from 'react-router-dom';
import './App.module.scss';
import Navbar from './components/Navbar/Navbar';

const App: React.FC = () => (
  <div className="app-container">
    <header>
      <Navbar />
    </header>
    <div className="main-content">
      <Outlet />
    </div>
  </div>
);

export default App
