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
import Tag from '../../components/Tag/Tag';

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
  const [isFiltersVisible, setIsFiltersVisible] = useState(false);
  const [totalPages, setTotalPages] = useState<number>(0);

  const languageDropdownRef = useRef<HTMLDivElement>(null);
  const visibilityDropdownRef = useRef<HTMLDivElement>(null);
  const perPageDropdownRef = useRef<HTMLDivElement>(null);
  const [isLanguageDropdownOpen, setIsLanguageDropdownOpen] = useState(false);
  const [isVisibilityDropdownOpen, setIsVisibilityDropdownOpen] = useState(false);
  const [isPerPageDropdownOpen, setIsPerPageDropdownOpen] = useState(false);

  useOnClickOutside(languageDropdownRef as React.RefObject<HTMLElement>, () => {
    setIsLanguageDropdownOpen(false);
  });

  useOnClickOutside(visibilityDropdownRef as React.RefObject<HTMLElement>, () => {
    setIsVisibilityDropdownOpen(false);
  });

  useOnClickOutside(perPageDropdownRef as React.RefObject<HTMLElement>, () => {
    setIsPerPageDropdownOpen(false);
  });

  const location = useLocation();
  const navigate = useNavigate();

  const getFiltersFromURL = (): FiltersType => {
    const params = new URLSearchParams(location.search);

    const tags = [...new Set(params.getAll('tags'))];

    return {
      page: params.get('page') ? Number(params.get('page')) : 1,
      per_page: params.get('per_page') ? Number(params.get('per_page')) : 10,
      tags: tags.length > 0 ? tags : undefined,
      language: params.get('language') || undefined,
      created_before: params.get('created_before') || undefined,
      created_after: params.get('created_after') || undefined,
      username: params.get('username') || undefined,
      visibility: params.get('visibility') === undefined
        ? undefined
        : (params.get('visibility') === 'public'
          ? 'public'
          : (params.get('visibility') === 'private'
            ? 'private'
            : undefined)),
    };
  };

  const filters = getFiltersFromURL();
  const [currentTag, setCurrentTag] = useState('');

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

  function handleAddTag(tagContent: string) {
    const trimmedTag = tagContent.trim();
    if (
      trimmedTag.length >= 2 &&
      (!filters.tags || filters.tags.length < 10) &&
      !(filters.tags && filters.tags.includes(trimmedTag))
    ) {
      const newTags = Array.isArray(filters.tags)
        ? [...filters.tags, trimmedTag]
        : [trimmedTag];
      handleFiltersChange('tags', newTags);
    }
    setCurrentTag('');
  }

  function handleFiltersChange(key: keyof FiltersType, value: any) {
    const nextPage = key === 'page' ? value : 1;

    const params = new URLSearchParams(location.search);

    switch (key) {
      case 'language':
        if (value !== undefined && value !== null && value !== '') {
          params.set('language', value.toLowerCase());
        } else {
          params.delete('language');
        }
        setIsLanguageDropdownOpen(false);
        break;
      case 'visibility':
        if (value === 'private') {
          params.set('visibility', 'private');
        } else if (value === 'public') {
          params.set('visibility', 'public');
        } else {
          params.delete('visibility');
        }
        setIsVisibilityDropdownOpen(false);
        break;
      case 'tags':
        params.delete('tags');
        if (Array.isArray(value) && value.length > 0) {
          value.forEach((tag: string) => {
            params.append('tags', tag);
          });
        }
        break;
      case 'created_before':
        if (value) {
          params.set('created_before', value);
        } else {
          params.delete('created_before');
        }
        break;
      case 'created_after':
        if (value) {
          params.set('created_after', value);
        } else {
          params.delete('created_after');
        }
        break;
      case 'username':
        if (value) {
          params.set('username', value);
        } else {
          params.delete('username');
        }
        break;
      case 'per_page': {

        params.set('per_page', String(value));

        setIsPerPageDropdownOpen(false);
        break;
      }
      case 'page':
        if (value && value >= 1) {
          if (value !== 1) {
            params.set('page', String(value));
          } else {
            params.delete('page');
          }
        } else {
          params.delete('page');
        }
        break;
      default:
        break;
    }

    if (key !== 'page') {
      if (nextPage !== 1) {
        params.set('page', String(nextPage));
      } else {
        params.delete('page');
      }
    }

    if (key !== 'per_page') {
      const currentPerPage = filters.per_page ?? 10;
      if (currentPerPage !== 10) {
        params.set('per_page', String(currentPerPage));
      } else {
        params.delete('per_page');
      }
    }

    let updatedFilters = { ...filters, [key]: value, page: nextPage };
    if (key === 'language' && typeof value === 'string') {
      updatedFilters.language = value;
    }
    if (key === 'tags' && (!value || value.length === 0)) {
      updatedFilters.tags = undefined;
    }

    navigate(`${location.pathname}?${params.toString()}`, { replace: true });
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

      setIsLoading(true);
      fetchSnippets(currentURLFilters);
    }
  }, [isTokenLoading, accessToken, isAuthenticated, location.search]);

  useEffect(() => {
    const requestedPage = getFiltersFromURL().page;
    if (totalPages > 0 && requestedPage !== undefined) {
      if (requestedPage > totalPages) {
        const params = getParams();
        params.set('page', totalPages.toString());
        navigate({
          pathname: location.pathname,
          search: params.toString()
        }, { replace: true });
      }
    }
  }, [totalPages, location.pathname, navigate]);

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

        <label htmlFor="snippet-search" className="visually-hidden" id="snippet-search-label">
          Search your snippets
        </label>
        <input
          id="snippet-search"
          onChange={(event) => setSearchInputValue(event.target.value)}
          type="text"
          placeholder='Search your snippets...'
          value={searchInputValue}
          className={styles.input}
          aria-labelledby="snippet-search-label"
        />

        <section
          className={styles.filters}
          aria-labelledby="filter-search-section-heading"
        >
          <div className={styles.container}>
            <h3 id="filter-search-section-heading" className={styles.filtersTitle}>Filters</h3>
            <button
              className={styles.filtersButton}
              onClick={() => setIsFiltersVisible(prev => !prev)}
              aria-expanded={isFiltersVisible}
              aria-controls="filters-content"
              aria-pressed={isFiltersVisible}
              type="button"
            >
              {isFiltersVisible ? 'Hide Filters -' : 'Show Filters +'}
            </button>
          </div>

          <div
            className={`
              ${styles.filtersContent} 
              ${isFiltersVisible ? styles.filtersExpanded : styles.filtersCollapsed}
            `}
            id="filters-content"
            aria-hidden={!isFiltersVisible}
          >
            <div className={styles.filtersItem}>
              <label htmlFor="per-page-input">Items per Page</label>
              <div className="dropdown" ref={perPageDropdownRef}>
                <button
                  type="button"
                  className={`
                    dropdownTrigger
                    ${isPerPageDropdownOpen ? ' dropdownTriggerActive' : ''}
                  `}
                  aria-haspopup="listbox"
                  aria-expanded={isPerPageDropdownOpen}
                  aria-controls="per-page-listbox"
                  id="per-page-dropdown"
                  onClick={() => setIsPerPageDropdownOpen(prev => !prev)}
                >
                  {filters.per_page || 10}
                </button>
                {isPerPageDropdownOpen && (
                  <div className="dropdownMenu" role="listbox" id="per-page-listbox" aria-labelledby="per-page-dropdown">
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.per_page === 5}
                      onClick={() => handleFiltersChange('per_page', 5)}
                      tabIndex={0}
                    >
                      5
                    </button>
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.per_page === 10}
                      onClick={() => handleFiltersChange('per_page', 10)}
                      tabIndex={0}
                    >
                      10
                    </button>
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.per_page === 15}
                      onClick={() => handleFiltersChange('per_page', 15)}
                      tabIndex={0}
                    >
                      15
                    </button>
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.per_page === 20}
                      onClick={() => handleFiltersChange('per_page', 20)}
                      tabIndex={0}
                    >
                      20
                    </button>
                  </div>
                )}
              </div>
            </div>
            <div className={styles.filtersItem}>
              <label id="visibility-label">Visibility</label>
              <div className="dropdown" ref={visibilityDropdownRef}>
                <button
                  type="button"
                  className={`
                    dropdownTrigger
                    ${isVisibilityDropdownOpen ? ' dropdownTriggerActive' : ''}
                  `}
                  aria-haspopup="listbox"
                  aria-expanded={isVisibilityDropdownOpen}
                  aria-controls="visibility-listbox"
                  aria-labelledby="visibility-label"
                  id="visibility-dropdown"
                  onClick={() => setIsVisibilityDropdownOpen(prev => !prev)}
                >
                  {filters.visibility === undefined ? 'All' : filters.visibility.charAt(0).toUpperCase() + filters.visibility.slice(1) + ' Only'}
                </button>
                {isVisibilityDropdownOpen && (
                  <div
                    className="dropdownMenu"
                    role="listbox"
                    id="visibility-listbox"
                    aria-labelledby="visibility-dropdown visibility-label"
                  >
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.visibility === undefined}
                      onClick={() => handleFiltersChange('visibility', undefined)}
                      tabIndex={0}
                    >
                      All
                    </button>
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.visibility === 'public'}
                      onClick={() => handleFiltersChange('visibility', 'public')}
                      tabIndex={0}
                    >
                      Public Only
                    </button>
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.visibility === 'private'}
                      onClick={() => handleFiltersChange('visibility', 'private')}
                      tabIndex={0}
                    >
                      Private Only
                    </button>
                  </div>
                )}
              </div>
            </div>
            <div className={styles.filtersItem}>
              <label id="language-label">Language</label>
              <div className="dropdown" ref={languageDropdownRef}>
                <button
                  type="button"
                  className={`
                    dropdownTrigger
                    ${isLanguageDropdownOpen ? ' dropdownTriggerActive' : ''}
                  `}
                  aria-haspopup="listbox"
                  aria-expanded={isLanguageDropdownOpen}
                  aria-controls="language-listbox"
                  aria-labelledby="language-label"
                  id="language-dropdown"
                  onClick={() => setIsLanguageDropdownOpen(prev => !prev)}
                >
                  {filters.language
                    ? filters.language.charAt(0).toUpperCase() + filters.language.slice(1)
                    : 'All'}
                </button>
                {isLanguageDropdownOpen && (
                  <div className="dropdownMenu" role="listbox" id="language-listbox" aria-labelledby="language-dropdown language-label">
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={!filters.language}
                      onClick={() => handleFiltersChange('language', undefined)}
                      tabIndex={0}
                    >
                      All
                    </button>
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.language === 'JavaScript'}
                      onClick={() => handleFiltersChange('language', 'JavaScript')}
                      tabIndex={0}
                    >
                      JavaScript
                    </button>
                    <button
                      className="dropdownItem"
                      role="option"
                      aria-selected={filters.language === 'Python'}
                      onClick={() => handleFiltersChange('language', 'Python')}
                      tabIndex={0}
                    >
                      Python
                    </button>
                  </div>
                )}
              </div>
            </div>
            <div className={styles.filtersItem}>
              <label htmlFor="username-input">Username</label>
              <input
                id="username-input"
                type="text"
                placeholder="Enter username"
                value={filters.username || ''}
                onChange={e => handleFiltersChange('username', e.target.value)}
                aria-label="Username"
              />
            </div>
            <div className={styles.filtersItem}>
              <label htmlFor="created-before">Created Before</label>
              <input
                id="created-before"
                type="date"
                value={filters.created_before || ''}
                onChange={e => handleFiltersChange('created_before', e.target.value || undefined)}
                aria-label="Created before date"
              />
            </div>
            <div className={styles.filtersItem}>
              <label htmlFor="created-after">Created After</label>
              <input
                id="created-after"
                type="date"
                value={filters.created_after || ''}
                onChange={e => handleFiltersChange('created_after', e.target.value || undefined)}
                aria-label="Created after date"
              />
            </div>
          </div>
          <div
            className={`
              ${styles.filtersContent} 
              ${isFiltersVisible ? styles.filtersExpanded : styles.filtersCollapsed}
            `}
            aria-hidden={!isFiltersVisible}
          >
            <div className={styles.filtersItem}>
              <label htmlFor="tags">Tags (comma or Enter to add)</label>
              <input
                placeholder="e.g., react, hooks"
                type="text"
                id="tags"
                name="tags"
                autoComplete="off"
                aria-describedby="tags-hint"
                minLength={2}
                maxLength={20}
                value={currentTag}
                onChange={event => {
                  if (event.target.value.endsWith(',')) {
                    handleAddTag(event.target.value.slice(0, -1));
                  } else {
                    setCurrentTag(event.target.value);
                  }
                }}
                onKeyDown={event => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    handleAddTag(currentTag.trim());
                  }
                }}
                aria-label="Add tag"
              />
              <span id="tags-hint" hidden>
                Enter a tag, then press comma or Enter to add. Maximum 10 tags, minimum 2 characters per tag.
              </span>
              <div className={styles.tagsList}>
                {Array.isArray(filters.tags) && filters.tags.map(tag => (
                  <Tag
                    key={tag}
                    content={tag}
                    onClose={() => handleFiltersChange(
                      'tags',
                      filters.tags?.filter((item: string) => item !== tag)
                    )}
                  />
                ))}
              </div>
            </div>
          </div>
        </section>
      </div >

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
    </main >
  )
}

export default SnippetsPage;