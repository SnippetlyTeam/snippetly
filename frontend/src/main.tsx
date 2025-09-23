import { createRoot } from 'react-dom/client';
import './styles/base.scss';
import { Root } from './Root.tsx';

createRoot(document.getElementById('root')!).render(<Root />);
