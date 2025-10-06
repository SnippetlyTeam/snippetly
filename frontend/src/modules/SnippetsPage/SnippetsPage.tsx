import { useState } from 'react';
import MainButton from '../../components/MainButton/MainButton';
import styles from './SnippetsPage.module.scss';
import Snippet from '../../components/Snippet/Snippet';
import { useNavigate } from 'react-router-dom';

const SnippetsPage = () => {
  const [searchInputValue, setSearchInputValue] = useState('');
  const navigate = useNavigate();

  return (
    <main className={styles.main}>
      <div className={styles.head}>
        <div className={styles.headContent}>
          <h2>Snippets</h2>
          <MainButton 
            content='Create New' 
            style={{ width: '150px' }} 
            onClick={() => navigate('/snippets')}
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
        <Snippet />
        <Snippet />
        <Snippet />
        <Snippet />
        <Snippet />
      </div>
    </main>
  )
}

export default SnippetsPage;