import { useEffect, useState, useRef } from 'react';
import MainButton from '../../components/MainButton/MainButton';
import styles from './SnippetsPage.module.scss';
import Snippet from '../../components/Snippet/Snippet';
import type { SnippetType } from '../../types/SnippetType';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';
import { getAll } from '../../api/snippetsClient';
import toast, { type Toast } from 'react-hot-toast';
import CustomToast from '../../components/CustomToast/CustomToast';
import { useLocation, useNavigate } from 'react-router-dom';
import { useOnClickOutside } from '../shared/hooks/useOnClickOutside';
import type { FiltersType } from '../../types/FiltersType';

const SnippetsPage = () => {
  const SIBLING_COUNT = 2;
  const EDGE_COUNT = 2;

  const [searchInputValue, setSearchInputValue] = useState('');
  const {
    accessToken,
    isTokenLoading,
    isAuthenticated
  } = useAuthContext();

  const [snippets, setSnippets] = useState<SnippetType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [totalPages, setTotalPages] = useState<number>(0);

  const languageDropdownRef = useRef<HTMLDivElement>(null);
  const [isLanguageDropdownOpen, setIsLanguageDropdownOpen] = useState(false);

  useOnClickOutside(languageDropdownRef as React.RefObject<HTMLElement>, () => {
    setIsLanguageDropdownOpen(false);
  });

  const location = useLocation();
  const navigate = useNavigate();

  const getInitialFilters = (): FiltersType => {
    const params = new URLSearchParams(window.location.search);

    return {
      page: params.get('page') ? Number(params.get('page')) : 1,
      per_page: params.get('per_page') ? Number(params.get('per_page')) : 10,
      tags: params.getAll('tags') ?? [],
      language: params.get('language') || undefined,
      created_before: params.get('created_before') || undefined,
      created_after: params.get('created_after') || undefined,
      username: params.get('username') || undefined,
      visibility:
        params.get('visibility') === null
          ? undefined
          : params.get('visibility') === 'true',
    };
  };

  const [filters, setFilters] = useState<FiltersType>(getInitialFilters());

  const paramsRef = useRef<{ pageParam: number | undefined; perPageParam: number | undefined }>({
    pageParam: undefined,
    perPageParam: undefined,
  });

  function getParams() {
    return new URLSearchParams(location.search);
  }

  async function fetchSnippets(params: FiltersType) {
    if (!accessToken) {
      setSnippets([]);
      return;
    }

    setIsLoading(true);

    try {
      const response = await getAll(accessToken, params);

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

  function handleFiltersChange(newFilters: Partial<typeof filters>) {
    const nextPage = typeof newFilters.page === 'number' && !isNaN(newFilters.page) && newFilters.page > 0
      ? newFilters.page
      : 1;

    setFilters(prev => ({
      ...prev,
      ...newFilters,
      page: nextPage,
    }));

    const params = new URLSearchParams(location.search);

    if (newFilters.language !== undefined) {
      params.set('language', newFilters.language);
    } else {
      params.delete('language');
    }

    if (newFilters.visibility !== undefined) {
      params.set('is_private', newFilters.visibility ? 'true' : 'false');
    } else {
      params.delete('is_private');
    }

    if (newFilters.tags !== undefined) {
      if (Array.isArray(newFilters.tags) && newFilters.tags.length > 0) {
        params.set('tags', newFilters.tags.join(','));
      } else {
        params.delete('tags');
      }
    }

    params.set('page', String(nextPage));
    params.set('per_page', String(filters.per_page ?? 10));

    navigate(`${location.pathname}?${params.toString()}`, { replace: true });
    fetchSnippets({ ...filters, ...newFilters, page: nextPage });
  }

  function getPaginationItems(): (number | string)[] {
    const page = filters.page ?? 1;
    const pages: (number | string)[] = [];
    if (totalPages <= EDGE_COUNT * 2 + SIBLING_COUNT * 2 + 1) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
      return pages;
    }

    const startPages = [];
    for (let i = 1; i <= EDGE_COUNT; i++) {
      startPages.push(i);
    }
    const endPages = [];
    for (let i = totalPages - EDGE_COUNT + 1; i <= totalPages; i++) {
      endPages.push(i);
    }

    const safePage = typeof page === 'number' && page > 0 ? page : 1;

    const siblingsStart = Math.max(
      Math.min(
        safePage - SIBLING_COUNT,
        totalPages - EDGE_COUNT - SIBLING_COUNT * 2
      ),
      EDGE_COUNT + 1
    );
    const siblingsEnd = Math.min(
      Math.max(
        safePage + SIBLING_COUNT,
        EDGE_COUNT + SIBLING_COUNT * 2 + 1
      ),
      totalPages - EDGE_COUNT
    );

    pages.push(...startPages);

    if (siblingsStart > EDGE_COUNT + 1) {
      pages.push('...');
    }

    for (let i = siblingsStart; i <= siblingsEnd; i++) {
      pages.push(i);
    }

    if (siblingsEnd < totalPages - EDGE_COUNT) {
      pages.push('...');
    }

    pages.push(...endPages);

    return pages;
  };

  useEffect(() => {
    const params = getParams();
    const pageRaw = params.get('page');
    const perPageRaw = params.get('per_page') || params.get('perPage');
    paramsRef.current = {
      pageParam: pageRaw ? parseInt(pageRaw, 10) : undefined,
      perPageParam: perPageRaw ? parseInt(perPageRaw, 10) : undefined
    };
  }, [location.search]);

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
      let page = filters.page ?? 1;
      let perPage = 10;

      const pageParam = params.get('page');
      const perPageParam = params.get('per_page') || params.get('perPage');

      if (pageParam) {
        const parsedPage = parseInt(pageParam, 10);
        if (!isNaN(parsedPage) && parsedPage > 0) {
          page = parsedPage;
          setFilters(prev => ({
            ...prev,
            page: parsedPage,
          }));
        }
      }

      if (perPageParam) {
        const parsedPerPage = parseInt(perPageParam, 10);
        if (!isNaN(parsedPerPage) && parsedPerPage > 0 && parsedPerPage <= 20) {
          perPage = parsedPerPage;
          setFilters(prev => ({
            ...prev,
            per_page: parsedPerPage,
          }));
        }
      }

      setIsLoading(true);
      fetchSnippets({ ...filters, page, per_page: perPage });
    }
  }, [isTokenLoading, accessToken, isAuthenticated, location.search]);

  useEffect(() => {
    const requestedPage = paramsRef.current.pageParam;
    if (totalPages > 0 && requestedPage !== undefined) {
      if (requestedPage > totalPages) {
        setFilters(prev => ({
          ...prev,
          page: totalPages,
        }));

        const params = getParams();
        params.set('page', totalPages.toString());
        navigate({
          pathname: location.pathname,
          search: params.toString()
        }, { replace: true });
      } else if (requestedPage !== (filters.page ?? 1)) {
        setFilters(prev => ({
          ...prev,
          page: requestedPage,
        }));
      }
    }
  }, [totalPages, location.pathname, navigate, filters.page])

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

  const currentPage = filters.page ?? 1;

  return (
    <main className={styles.main} aria-labelledby="snippets-heading">
      <div className={styles.head}>
        <div className={styles.headContent}>
          <h2 id="snippets-heading">Snippets</h2>
          <MainButton
            content='Create New'
            style={{ width: '150px' }}
            onClick={() => navigate('/snippets/create')}
            aria-label="Create a new snippet"
          />
        </div>

        <label htmlFor="snippet-search" className="visually-hidden">
          Search your snippets
        </label>
        <input
          id="snippet-search"
          onChange={(event) => setSearchInputValue(event.target.value)}
          type="text"
          placeholder='Search your snippets...'
          value={searchInputValue}
          className={styles.input}
          aria-label="Search your snippets"
        />

        <section className={styles.filters} aria-labelledby="filter-search-section-heading">
          <h3 id="filter-search-section-heading" className={styles.filtersTitle}>Filters</h3>
          <div className={styles.line} />

          <div className={styles.filtersContent}>
            <div className={styles.filtersItem}>
              <strong id="snippet-lang-label">Language</strong>

              <div className='dropdown' ref={languageDropdownRef}>
                <button
                  className='dropdownTrigger'
                  onClick={() => setIsLanguageDropdownOpen(prev => !prev)}
                >All languages</button>

                {isLanguageDropdownOpen && (
                  <div className='dropdownMenu'>
                    <div className='dropdownItem'>Python</div>
                    <div className='dropdownItem'>JavaScript</div>
                  </div>
                )}
              </div>
            </div>
            <div className={styles.filtersItem}>
              <strong id="snippet-visibility-label">Visibility</strong>
            </div>
            <div className={styles.filtersItem}>
              <strong id="snippet-searchby-label">Search by</strong>
            </div>
          </div>
        </section>
      </div>

      <section
        className={styles.snippets}
        aria-label="List of code snippets"
        tabIndex={-1}
      >
        {isLoading ? (
          <Loader aria-label="Loading snippets" />
        ) : (
          Array.isArray(snippets) ? (
            snippets.length === 0 ? (
              <div role="status" aria-live="polite" style={{ color: '#d4d4d4', marginTop: '2rem' }}>
                No snippets found.
              </div>
            ) : (
              snippets.map((snippet: SnippetType) => (
                <Snippet key={snippet.uuid} snippet={snippet} />
              ))
            )
          ) : null
        )}
      </section>

      {(totalPages > 1 && !isLoading) && (
        <nav
          className={styles.pagination}
          aria-label="Pagination Navigation"
        >
          <button
            className={styles.paginationSwitcher}
            onClick={() => handleFiltersChange({ page: currentPage - 1 })}
            disabled={currentPage === 1}
            aria-disabled={currentPage === 1}
            aria-label="Previous page"
            tabIndex={currentPage === 1 ? -1 : 0}
          >
            &larr; Prev
          </button>

          <div className={styles.paginationPages} role="group" aria-label="Page numbers">
            {getPaginationItems().map((item, index) => (
              typeof item === 'number' ? (
                <button
                  key={item}
                  className={`
                    ${styles.paginationItem} 
                    ${currentPage === item ? styles.paginationItemActive : ''}
                  `}
                  onClick={() => handleFiltersChange({ page: item })}
                  disabled={currentPage === item}
                  aria-current={currentPage === item ? "page" : undefined}
                  aria-label={`Go to page ${item}`}
                  tabIndex={currentPage === item ? -1 : 0}
                >
                  {item}
                </button>
              ) : (
                <span
                  key={`ellipsis-${index}`}
                  className={styles.paginationEllipsis}
                  aria-hidden="true"
                  aria-label="ellipsis"
                >...</span>
              )
            ))}
          </div>

          <button
            className={styles.paginationSwitcher}
            onClick={() => handleFiltersChange({ page: currentPage + 1 })}
            disabled={currentPage === totalPages}
            aria-disabled={currentPage === totalPages}
            aria-label="Next page"
            tabIndex={currentPage === totalPages ? -1 : 0}
          >
            Next &rarr;
          </button>
        </nav>
      )}
    </main>
  )
}

export default SnippetsPage;