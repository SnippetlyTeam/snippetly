import { Link } from 'react-router-dom';
import styles from './Snippet.module.scss';
import type { SnippetType } from '../../types/SnippetType';
import Tag from '../Tag/Tag';
import { useSnippetContext } from '../../contexts/SnippetContext';
import Heart from '../Heart/Heart';
import { addFavorite, removeFavorite } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';

type Props = {
  snippet: SnippetType,
}

const Snippet: React.FC<Props> = ({ snippet }) => {
  const { favoriteSnippetsIds, setFavoriteSnippetsIds } = useSnippetContext();
  const { accessToken } = useAuthContext();

  function handleHeartClick(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();
    event.stopPropagation();

    if (favoriteSnippetsIds.includes(snippet.uuid)) {
      removeFavorite(accessToken, snippet.uuid);
      setFavoriteSnippetsIds(prev => prev.filter(id => id !== snippet.uuid));
    } else {
      addFavorite(accessToken, snippet.uuid);
      setFavoriteSnippetsIds(prev => [...prev, snippet.uuid]);
    }
  }

  return (
    <Link
      to={`/snippets/${snippet.uuid}`}
      className={styles.snippet}
    >
      <div className={styles.head}>
        <div className={styles.container}>
          <h3 className={styles.title}>{snippet.title}</h3>
          <button
            className={styles.button}
            onClick={handleHeartClick}
          >
            <Heart isFilled={favoriteSnippetsIds.includes(snippet.uuid)} />
          </button>
        </div>
        <p className={styles.language}>Language: {snippet.language}</p>
      </div>

      <div className={styles.content}>
        {snippet.content}
      </div>

      <div className={styles.line} />

      <div className={styles.tags}>
        {snippet.tags.map(tag => (
          <Tag content={tag} key={tag} />
        ))}
      </div>
    </Link>
  );
}

export default Snippet;