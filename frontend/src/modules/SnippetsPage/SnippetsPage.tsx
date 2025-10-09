import { useEffect, useState } from 'react';
import MainButton from '../../components/MainButton/MainButton';
import styles from './SnippetsPage.module.scss';
import Snippet from '../../components/Snippet/Snippet';
import type { SnippetType } from '../../types/SnippetType';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';
import { getAll } from '../../api/snippetsClient';
import toast, { type Toast } from 'react-hot-toast';
import CustomToast from '../../components/CustomAuthToast/CustomToast';
import { useLocation, useNavigate } from 'react-router-dom';

const SnippetsPage = () => {
  const [searchInputValue, setSearchInputValue] = useState('');
  const { accessToken, isTokenLoading, isAuthenticated } = useAuthContext();

  const [data, setData] = useState<{} | null>(null);
  const [snippets, setSnippets] = useState<SnippetType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchSnippets = async () => {
    if (!accessToken) {
      setData({ snippets: [] });
      setSnippets([]);
      setIsLoading(false);
      return;
    }
    try {
      const response = await getAll(accessToken);

      setData(response.data);
      if (Array.isArray(response.data)) {
        setSnippets(response.data);
      } else if (response.data && Array.isArray(response.data.snippets)) {
        setSnippets(response.data.snippets);
      } else {
        setSnippets([]);
      }
    } catch (error) {
      setData({ snippets: [] });
      setSnippets([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isTokenLoading) {
      setIsLoading(true);
      return;
    }

    if (!isAuthenticated) {
      setIsLoading(false);
      return;
    }

    if (accessToken) {
      setIsLoading(true);
      fetchSnippets();
    }

  }, [isTokenLoading, accessToken, isAuthenticated]);

  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (
      location.state &&
      (location.state.title || location.state.message || location.state.type)
    ) {
      const { title = '', message = '', type = 'info' } = location.state || {};

      toast.custom((t: Toast) => (
        <CustomToast
          t={t}
          title={title}
          message={message}
          type={type}
        />
      ), {
        duration: 2500,
      });

      navigate(location.pathname, { replace: true, state: null });
    }
  }, [location, navigate]);

  return (
    <main className={styles.main}>
      <div className={styles.head}>
        <div className={styles.headContent}>
          <h2>Snippets</h2>
          <MainButton
            content='Create New'
            style={{ width: '150px' }}
            onClick={() => navigate('/snippets/create')}
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