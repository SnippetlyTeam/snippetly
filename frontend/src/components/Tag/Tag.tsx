import styles from './Tag.module.scss';

type Props = {
  content: string
  onClose?: () => void
}

const Tag: React.FC<Props> = ({ content, onClose }) => {
  return (
    <div className={styles.tag}>
      <span>{content}</span>

      {onClose && (
        <button
          className={styles.removeButton}
          aria-label="Remove tag" type="button"
          onClick={onClose}
        >
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
            <line x1="4.47" y1="4.47" x2="11.53" y2="11.53" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
            <line x1="11.53" y1="4.47" x2="4.47" y2="11.53" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
          </svg>
        </button>
      )}
    </div>
  )
}

export default Tag;