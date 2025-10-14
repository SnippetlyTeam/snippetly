import type { FiltersType } from '../../types/FiltersType';
import styles from './SnippetsPage.module.scss';

type Props = {
  totalPages: number;
  currentPage: number;
  paginationItems: (string | number)[]
  handleFiltersChange: (key: keyof FiltersType, value: any) => void;
}

const Pagination: React.FC<Props> = ({
  totalPages,
  currentPage,
  paginationItems,
  handleFiltersChange
}) => (
  <nav
    className={styles.pagination}
    aria-label="Pagination Navigation"
  >
    <button
      className={styles.paginationSwitcher}
      onClick={() => handleFiltersChange('page', currentPage - 1)}
      disabled={currentPage === 1}
      aria-disabled={currentPage === 1}
      aria-label="Previous page"
      tabIndex={currentPage === 1 ? -1 : 0}
    >
      &larr; Prev
    </button>

    <div className={styles.paginationPages} role="group" aria-label="Page numbers">
      {paginationItems.map((item, index) => (
        typeof item === 'number' ? (
          <button
            key={item}
            className={`
                  ${styles.paginationItem} 
                  ${currentPage === item ? styles.paginationItemActive : ''}
                `}
            onClick={() => handleFiltersChange('page', item)}
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
      onClick={() => handleFiltersChange('page', currentPage + 1)}
      disabled={currentPage === totalPages}
      aria-disabled={currentPage === totalPages}
      aria-label="Next page"
      tabIndex={currentPage === totalPages ? -1 : 0}
    >
      Next &rarr;
    </button>
  </nav>
)
export default Pagination;