import { useEffect, useState } from 'react';
import styles from './SnippetFormPage.module.scss';
import CodeEditor from '../../components/CodeEditor/CodeEditor';
import type { SnippetLanguageType } from '../../types/SnippetLanguageType';
import MainButton from '../../components/MainButton/MainButton';
import { create, getById, update } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useParams } from 'react-router-dom';
import { Loader } from '../../components/Loader';

const SnippetFormPage = () => {
  const { snippetId } = useParams();
  const isEditMode = !!snippetId;

  const [isLanguageDropDownOpen, setIsLanguageDropdownOpen] = useState(false);
  const languages: string[] = ['JavaScript', 'Python'];
  const { accessToken } = useAuthContext();

  const [title, setTitle] = useState('');
  const [language, setLanguage] = useState(languages[0]);
  const [content, setContent] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(isEditMode);

  function handleLanguageChange(lang: string) {
    setLanguage(lang);
    setIsLanguageDropdownOpen(false);
  }

  function formatLanguage(language: string): SnippetLanguageType {
    switch (language) {
      case 'JavaScript':
        return 'js';
      case 'Python':
        return 'py';
      default:
        return 'js';
    }
  }

  function validateForm() {
    if (!title) {
      return false;
    }

    if (!content) {
      return false;
    }

    return true;
  }

  async function handleSnippetSave(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (isEditMode) {
      await update(snippetId, {
        title,
      }, accessToken);
      return;
    }

    await create({
      title,
      language: language.toLowerCase(),
      is_private: isPrivate,
      content,
      description,
    }, accessToken);
  }

  useEffect(() => {
    if (isEditMode) {
      getById(snippetId, accessToken)
        .then(response => {
          if (response.status === 200) {
            setTitle(response.data.title);
            setLanguage(response.data.language);
            setIsPrivate(response.data.is_private);
            setContent(response.data.content);
            setDescription(response.data.description);
          }
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, []);

  return (
    <main className={styles.main}>
      <h2>Create a New Snippet</h2>

      {isLoading ? (
        <Loader />
      ) : (
        <form className={styles.form} noValidate onSubmit={handleSnippetSave}>
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
                  {language}
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
              language={formatLanguage(language)}
            />
          </div>

          <MainButton content='Save Snippet' type="submit" />
        </form>
      )}
    </main>
  )
}

export default SnippetFormPage;