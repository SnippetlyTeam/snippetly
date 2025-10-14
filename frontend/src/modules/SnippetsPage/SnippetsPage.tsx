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
import Pagination from './Pagination';

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
  const [isVisibilityDropdownOpen, setIsVisibilityDropdownOpen] = useState(false);

  useOnClickOutside(languageDropdownRef as React.RefObject<HTMLElement>, () => {
    setIsLanguageDropdownOpen(false);
  });

  const location = useLocation();
  const navigate = useNavigate();

  const getFiltersFromURL = (): FiltersType => {
    const params = new URLSearchParams(location.search);

    const tags = params.getAll('tags');

    return {
      page: params.get('page') ? Number(params.get('page')) : 1,
      per_page: params.get('per_page') ? Number(params.get('per_page')) : 10,
      tags: tags.length > 0 ? tags : undefined,
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

  const [filters, setFilters] = useState<FiltersType>(getFiltersFromURL());

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
    const nextPage =
      typeof newFilters.page === 'number' && !isNaN(newFilters.page) && newFilters.page > 0
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

    const currentTags =
      newFilters.tags !== undefined
        ? newFilters.tags
        : filters.tags;

    params.delete('tags');
    if (Array.isArray(currentTags) && currentTags.length > 0) {
      currentTags.forEach(tag => {
        params.append('tags', tag);
      });
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
      const currentURLFilters = getFiltersFromURL();

      setFilters(currentURLFilters);
      setIsLoading(true);
      fetchSnippets(currentURLFilters);
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
              <label>Items per Page</label>
              <input type="text" />
            </div>
            <div className={styles.filtersItem}>
              <label>Visibility</label>
              <div className="dropdown">
                <button
                  type="button"
                  className="dropdownTrigger"
                  aria-haspopup="listbox"
                  aria-expanded="false"
                  onClick={() => setIsVisibilityDropdownOpen(prev => !prev)}
                >
                  {filters.visibility || 'All'}
                </button>
                {isVisibilityDropdownOpen && (
                  <div className="dropdownMenu" role="listbox">
                    <div
                      className="dropdownItem"
                      role="option"
                      aria-selected={!filters.language}
                      onClick={() => handleFiltersChange({ language: undefined })}
                      tabIndex={0}
                    >
                      All
                    </div>
                    <div
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.language === 'JavaScript'}
                      onClick={() => handleFiltersChange({ language: 'JavaScript' })}
                      tabIndex={0}
                    >
                      Public
                    </div>
                    <div
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.language === 'Python'}
                      onClick={() => handleFiltersChange({ language: 'Python' })}
                      tabIndex={0}
                    >
                      Private
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className={styles.filtersItem}>
              <label>Language</label>
              <div className="dropdown">
                <button
                  type="button"
                  className="dropdownTrigger"
                  aria-haspopup="listbox"
                  aria-expanded="false"
                  onClick={() => setIsLanguageDropdownOpen(prev => !prev)}
                >
                  {filters.language || 'All'}
                </button>
                {isLanguageDropdownOpen && (
                  <div className="dropdownMenu" role="listbox">
                    <div
                      className="dropdownItem"
                      role="option"
                      aria-selected={!filters.language}
                      onClick={() => handleFiltersChange({ language: undefined })}
                      tabIndex={0}
                    >
                      All
                    </div>
                    <div
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.language === 'JavaScript'}
                      onClick={() => handleFiltersChange({ language: 'JavaScript' })}
                      tabIndex={0}
                    >
                      JavaScript
                    </div>
                    <div
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.language === 'Python'}
                      onClick={() => handleFiltersChange({ language: 'Python' })}
                      tabIndex={0}
                    >
                      Python
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className={styles.filtersItem}>
              <label>Username</label>
              <input type="text" />
            </div>
            <div className={styles.filtersItem}>
              <label htmlFor="created-before">Created Before</label>
              <input
                id="created-before"
                type="date"
                value={filters.created_before || ''}
                onChange={e => handleFiltersChange({ created_before: e.target.value || undefined })}
              />
            </div>
            <div className={styles.filtersItem}>
              <label htmlFor="created-after">Created After</label>
              <input
                id="created-after"
                type="date"
                value={filters.created_after || ''}
                onChange={e => handleFiltersChange({ created_after: e.target.value || undefined })}
              />
            </div>
          </div>

          <div className={styles.line} />
          <div className={styles.filtersContent}>
            <div className={styles.filtersItem}>
              <label htmlFor="">Tags</label>
              <input type="text" />
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
        <Pagination
          totalPages={totalPages}
          paginationItems={getPaginationItems()}
          currentPage={filters.page ?? 1}
          handleFiltersChange={handleFiltersChange}
        />
      )}
    </main>
  )
}

export default SnippetsPage;