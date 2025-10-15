import { useNavigate } from 'react-router-dom';
import styles from './Snippet.module.scss';
import type { SnippetType } from '../../types/SnippetType';
import Tag from '../Tag/Tag';

type Props = {
  snippet: SnippetType,
}

const Snippet: React.FC<Props> = ({ snippet }) => {
  const navigate = useNavigate();

  return (
    <button
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

      <div className={styles.tags}>
        {snippet.tags.map(tag => (
          <Tag content={tag} key={tag}/>
        ))}
      </div>
    </button>
  );
}

export default Snippet;