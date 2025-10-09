import styles from './SnippetFormPage.module.scss';

type Props = {
  currentLength: number;
  maxLength: number;
}

const CharacterCountIndicator: React.FC<Props> = ({ currentLength, maxLength }) => (
  <span className={styles.hint}>
    {`${currentLength} / ${maxLength}`}
  </span>
)

export default CharacterCountIndicator;