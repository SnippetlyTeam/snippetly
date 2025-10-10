import { useNavigate } from 'react-router-dom';
import styles from './Snippet.module.scss';
import type { SnippetType } from '../../types/SnippetType';

type Props = {
  snippet: SnippetType,
}

const Snippet: React.FC<Props> = ({ snippet }) => {
  const navigate = useNavigate();

  return (
    <div
      className={styles.snippet}
      onClick={() => navigate(`/snippets/${snippet.uuid}`)}
    >
      <div className={styles.head}>
        <h3 className={styles.title}>{snippet.title}</h3>
        <p className={styles.language}>Language: {snippet.language}</p>
      </div>

      <div className={styles.content}>
        {snippet.content}
      </div>

      <div className={styles.line} />

      <div className={styles.tags}></div>
    </div>
  );
}

export default Snippet;