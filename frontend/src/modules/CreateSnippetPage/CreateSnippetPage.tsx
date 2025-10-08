import { useState } from 'react';
import styles from './CreateSnippetPage.module.scss';
import CodeEditor from '../../components/CodeEditor/CodeEditor';
import type { SnippetLanguageType } from '../../types/SnippetLanguageType';
import MainButton from '../../components/MainButton/MainButton';
import { create } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';

const CreateSnippetPage = () => {
  const [isLanguageDropDownOpen, setIsLanguageDropdownOpen] = useState(false);
  const languages: string[] = ['JavaScript', 'Python', 'React'];
  const { accessToken } = useAuthContext();

  const [currentLanguage, setCurrentLanguage] = useState(languages[0]);

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [description, setDescription] = useState('');

  function handleLanguageChange(lang: string) {
    setCurrentLanguage(lang);
    setIsLanguageDropdownOpen(false);
  }

  function formatLanguage(language: string): SnippetLanguageType {
    switch (language) {
      case 'JavaScript':
        return 'js';
      case 'React':
        return 'jsx';
      case 'Python':
        return 'py';
      default:
        return 'js';
    }
  }

  async function handleSnippetSave() {
    const response = await create({
      title,
      language: currentLanguage,
      is_private: isPrivate,
      content,
      description,
    }, accessToken);
  }

  return (
    <main className={styles.main}>
      <h2>Create a New Snippet</h2>

      <form className={styles.form} noValidate>
        <div className={styles.formItem}>
          <label htmlFor="title">Title</label>
          <input
            className={styles.input}
            type="text"
            id='title'
            placeholder='Enter snippet title'
            value={title}
            onChange={event => setTitle(event.target.value)}
            required
          />
        </div>

        <div className={styles.container}>
          <div className={styles.formItem}>
            <label htmlFor="language">Language</label>
            <div className={styles.dropdown}>
              <button
                type="button"
                className={`
              ${styles.dropdownTrigger} 
              ${isLanguageDropDownOpen ? styles.dropdownTriggerActive : ''}
            `}
                onClick={() => setIsLanguageDropdownOpen(prev => !prev)}
              >
                {currentLanguage}
              </button>

              {isLanguageDropDownOpen && (
                <div className={styles.dropdownMenu}>
                  {languages.map(lang => (
                    <button
                      key={lang}
                      type="button"
                      onClick={() => handleLanguageChange(lang)}
                      className={styles.dropdownItem}
                    >
                      {lang}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className={styles.formItem}>
            <label htmlFor="tags">Tags</label>
            <input
              placeholder='e.g., react, hooks'
              type="text"
              id='tags'
            />
          </div>
        </div>

        <div className={styles.fromItem}>
          <label htmlFor="code">Code</label>
          <CodeEditor
            value={content}
            setValue={setContent}
            language={formatLanguage(currentLanguage)}
          />
        </div>

        <MainButton content='Save Snippet' onClick={handleSnippetSave} />
      </form>
    </main>
  )
}

export default CreateSnippetPage;