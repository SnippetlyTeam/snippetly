import type { FiltersType } from '../../types/FiltersType';
import styles from './Pagination.module.scss';

type Props = {
  totalPages: number;
  currentPage: number;
  onPageChange: (key: keyof FiltersType, value: any) => void;
}

const Pagination: React.FC<Props> = ({
  totalPages,
  currentPage,
  onPageChange,
}) => {
  const SIBLING_COUNT = 2;
  const EDGE_COUNT = 2;

  function getPaginationItems(): (number | string)[] {
    const page = currentPage ?? 1;
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

  return (
    <nav
      className={styles.pagination}
      aria-label="Pagination Navigation"
    >
      <button
        className={styles.paginationSwitcher}
        onClick={() => onPageChange('page', currentPage - 1)}
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
              onClick={() => onPageChange('page', item)}
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
        onClick={() => onPageChange('page', currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-disabled={currentPage === totalPages}
        aria-label="Next page"
        tabIndex={currentPage === totalPages ? -1 : 0}
      >
        Next &rarr;
      </button>
    </nav>
  )
}
export default Pagination;