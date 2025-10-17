import styles from './FavoritesPage.module.scss';
import { useSnippetContext } from "../../contexts/SnippetContext";
import { getById } from "../../api/snippetsClient";
import { useAuthContext } from '../../contexts/AuthContext';
import type { SnippetDetailsType } from '../../types/SnippetDetailsType';
import Snippet from '../../components/Snippet/Snippet';
import { useQuery } from '@tanstack/react-query';
import { Loader } from '../../components/Loader';

const FavoritesPage = () => {
  const { favoriteSnippetsIds } = useSnippetContext();
  const { accessToken } = useAuthContext();

  const {
    data: snippets = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['favoriteSnippets', favoriteSnippetsIds, accessToken],
    queryFn: async () => {
      if (favoriteSnippetsIds.length === 0) {
        return [];
      }
      const responses = await Promise.all(
        favoriteSnippetsIds.map(id => getById(id, accessToken))
      );
      return responses
        .map(response => response?.data)
        .filter(Boolean) as SnippetDetailsType[];
    },
    enabled: !!accessToken,
  });

  return (
    <main className={styles.main}>
      <h2>Favorite Snippets</h2>

      {isLoading ? (
        <Loader />
      ) : isError ? (
        <div>Failed to load your favorite snippets. Please try again later.</div>
      ) : favoriteSnippetsIds.length === 0 ? (
        <div>You haven&apos;t added any snippets to your favorites yet.</div>
      ) : snippets.length === 0 ? (
        <div>
          Could not load your favorite snippets or they may have been removed.
        </div>
      ) : (
        <div className={styles.snippets}>
          {snippets.map(snippet => (
            <Snippet key={snippet.uuid} snippet={snippet} />
          ))}
        </div>
      )}
    </main>
  );
}

export default FavoritesPage;