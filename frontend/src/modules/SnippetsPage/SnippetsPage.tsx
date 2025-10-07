import { useEffect, useState } from 'react';
import MainButton from '../../components/MainButton/MainButton';
import styles from './SnippetsPage.module.scss';
import Snippet from '../../components/Snippet/Snippet';
import type { SnippetType } from '../../types/SnippetType';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';

const SnippetsPage = () => {
  const SERVER_BASE_URL = import.meta.env.VITE_SERVER_BASE_URL;

  const [searchInputValue, setSearchInputValue] = useState('');
  const { accessToken } = useAuthContext();

  const [data, setData] = useState<{} | null>(null);
  const [snippets, setSnippets] = useState<SnippetType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchSnippets = async () => {
    try {
      const response = await fetch(`${SERVER_BASE_URL}/api/v1/snippets`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch snippets');
      }
      const result = await response.json();
      setData(result);
      setSnippets(result.snippets)
    } catch (error) {
      setData({ snippets: [] });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setIsLoading(true);
    fetchSnippets();
  }, []);

  return (
    <main className={styles.main}>
      <div className={styles.head}>
        <div className={styles.headContent}>
          <h2>Snippets</h2>
          <MainButton
            content='Create New'
            style={{ width: '150px' }}
            onClick={() => {
              fetch(`${SERVER_BASE_URL}/api/v1/snippets/create`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify({
                  title: 'Untitled',
                  language: 'python',
                  is_private: false,
                  content: 'string',
                  description: 'string',
                }),
              })
                .then(response => response.json())
                .then(data => setSnippets(prev => [data, ...prev]));
            }}
          />
        </div>

        <input
          onChange={(event) => setSearchInputValue(event.target.value)}
          type="text"
          placeholder='Search your snippets...'
          value={searchInputValue}
          className={styles.input}
        />
      </div>

      <div className={styles.snippets}>
        {isLoading ? (
          <Loader />
        ) : (
          Array.isArray(snippets) ? (
            snippets.map((snippet: SnippetType) => (
              <Snippet key={snippet.uuid} snippet={snippet} />
            ))
          ) : null
        )}
      </div>
    </main>
  )
}

export default SnippetsPage;