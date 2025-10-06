import { useNavigate } from 'react-router-dom';
import styles from './Snippet.module.scss';

const Snippet = () => {
  const navigate = useNavigate();

  return (
    <div 
      className={styles.snippet}
      onClick={() => navigate(`/snippets/2`)}
    ></div>
  );
}

export default Snippet;