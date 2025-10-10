import styles from './Tag.module.scss';

type Props = {
  content: string
}

const Tag: React.FC<Props> = ({ content }) => {
  return (
    <div className={styles.tag}>
      {content}
    </div>
  )
}

export default Tag;