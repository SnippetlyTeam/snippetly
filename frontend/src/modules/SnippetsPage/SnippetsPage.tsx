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
  const {
    accessToken,
    isTokenLoading,
    isAuthenticated
  } = useAuthContext();

  const [snippets, setSnippets] = useState<SnippetType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [perPageValue, setPerPageValue] = useState(10);
  const [totalPages, setTotalPages] = useState<number>(0);

  const location = useLocation();
  const navigate = useNavigate();

  function getParams() {
    return new URLSearchParams(location.search);
  }

  async function fetchSnippets(page: number, perPage: number) {
    if (!accessToken) {
      setSnippets([]);
      return;
    }

    setIsLoading(true);

    try {
      const response = await getAll(accessToken, page, perPage);

      if (response.data && Array.isArray(response.data.snippets)) {
        setSnippets(response.data.snippets);
        setTotalPages(response.data.total_pages);
      } else {
        setSnippets([]);
      }
    } catch (error) {
      setSnippets([]);
    } finally {
      setIsLoading(false);
    }
  };

  function handlePageChange(newValue: number) {
    if (newValue >= 1 && newValue <= totalPages) {
      fetchSnippets(newValue, perPageValue);
      setCurrentPage(newValue);
    }
  }

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
      const params = getParams();
      let page = currentPage;
      let perPage = 10;

      const pageParam = params.get('page');
      const perPageParam = params.get('perPage');

      if (pageParam) {
        const parsedPage = parseInt(pageParam, 10);
        if (!isNaN(parsedPage) && parsedPage > 0 && parsedPage <= totalPages) {
          page = parsedPage;
          setCurrentPage(parsedPage);
        }
      }

      if (perPageParam) {
        const parsedPerPage = parseInt(perPageParam, 10);
        if (!isNaN(parsedPerPage) && parsedPerPage > 0 && parsedPerPage <= 20) {
          perPage = parsedPerPage;
          setPerPageValue(parsedPerPage);
        }
      }

      setIsLoading(true);
      fetchSnippets(page, perPage);
    }
  }, [isTokenLoading, accessToken, isAuthenticated, location.search]);

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

      {totalPages > 1 && (
        <div className={styles.pagination}>
          <button
            className={styles.paginationSwitcher}
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            &larr; Prev
          </button>

          <div className={styles.paginationPages}>
            {
              Array.from({ length: totalPages }, (_, i) => (
                <button
                  key={i + 1}
                  className={`${styles.paginationItem} ${currentPage === i + 1 ? styles.paginationItemActive : ''}`}
                  onClick={() => handlePageChange(i + 1)}
                  disabled={currentPage === i + 1}
                >
                  {i + 1}
                </button>
              ))
            }
          </div>

          <button
            className={styles.paginationSwitcher}
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next &rarr;
          </button>
        </div>
      )}
    </main>
  )
}

export default SnippetsPage;