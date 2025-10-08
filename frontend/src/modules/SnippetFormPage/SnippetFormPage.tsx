import { useEffect, useRef, useState } from 'react';
import styles from './SnippetFormPage.module.scss';
import CodeEditor from '../../components/CodeEditor/CodeEditor';
import MainButton from '../../components/MainButton/MainButton';
import { create, getById, update } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useParams } from 'react-router-dom';
import { Loader } from '../../components/Loader';
import { useOnClickOutside } from '../shared/hooks/useOnClickOutside';
import type { NewSnippetType } from '../../types/NewSnippetType';
import type { SnippetType } from '../../types/SnippetType';
import { useMutation } from '@tanstack/react-query';

const SnippetFormPage = () => {
  const { snippetId } = useParams();
  const isEditMode = !!snippetId;
  const languages: string[] = ['JavaScript', 'Python'];

  const emptySnippet: NewSnippetType = {
    title: '',
    language: languages[0],
    is_private: false,
    content: '',
    description: '',
  }

  const [isLanguageDropDownOpen, setIsLanguageDropdownOpen] = useState(false);
  const { accessToken } = useAuthContext();

  const dropdownRef = useRef<HTMLDivElement>(null);

  const {
    mutate: createSnippet,
    isPending: isCreating,
  } = useMutation({
    mutationFn: (newSnippet: NewSnippetType) => create(newSnippet, accessToken),
    onSuccess: (response) => setSnippet(response.data),
  });

  const {
    mutate: updateSnippet,
    isPending: isUpdating,
  } = useMutation({
    mutationFn: (newSnippet: NewSnippetType) => {
      return update(snippetId as string, newSnippet, accessToken)
    },
    onSuccess: (response) => {
      setSnippet(response.data);
    },
  });

  useOnClickOutside(dropdownRef as React.RefObject<HTMLElement>, () => {
    setIsLanguageDropdownOpen(false);
  });

  const [snippet, setSnippet] = useState<NewSnippetType | SnippetType>(emptySnippet);

  const [isLoading, setIsLoading] = useState(isEditMode);

  function handleLanguageChange(lang: string) {
    setSnippet(prev => ({
      ...prev,
      language: lang
    }));
    setIsLanguageDropdownOpen(false);
  }

  function formatLanguage(language: string): string {
    switch (language.toLowerCase()) {
      case 'javascript':
        return 'JavaScript';
      case 'python':
        return 'Python';
      case 'JavaScript':
        return 'javascript';
      case 'Python':
        return 'python';
      default:
        return 'javascript';
    }
  }

  function handleContentChange(value: string) {
    setSnippet(prev => ({
      ...prev,
      content: value,
    }));
  }

  async function handleSnippetSave(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!snippet) return;

    if (isEditMode) {
      updateSnippet({
        title: snippet.title,
        language: snippet.language.toLowerCase(),
        is_private: snippet.is_private,
        content: snippet.content,
        description: snippet.description,
      });
      return;
    }

    createSnippet({
      title: snippet.title,
      language: snippet.language.toLowerCase(),
      is_private: snippet.is_private,
      content: snippet.content,
      description: snippet.description,
    });
  }

  useEffect(() => {
    if (isEditMode) {
      getById(snippetId, accessToken)
        .then(response => {
          if (response.status === 200) {
            setSnippet(response.data);
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
              value={snippet.title ?? ''}
              onChange={event =>
                setSnippet(prev =>
                  prev
                    ? { ...prev, title: event.target.value }
                    : {
                      title: event.target.value,
                      language: '',
                      is_private: false,
                      content: '',
                      description: '',
                    }
                )
              }
              required
            />
          </div>

          <div className={styles.container}>
            <div className={styles.formItem}>
              <label htmlFor="language">Language</label>
              <div ref={dropdownRef} className={styles.dropdown}>
                <button
                  type="button"
                  className={`
                    ${styles.dropdownTrigger} 
                    ${isLanguageDropDownOpen ? styles.dropdownTriggerActive : ''}
                  `}
                  onClick={() => setIsLanguageDropdownOpen(prev => !prev)}
                >
                  {formatLanguage(snippet.language)}
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
              value={snippet.content}
              onChange={handleContentChange}
              language={formatLanguage(snippet.language)}
            />
          </div>

          <MainButton
            content={(isCreating || isUpdating) ? <Loader buttonContent /> : 'Save Snippet'}
            type="submit"
          />
        </form>
      )}
    </main>
  )
}

export default SnippetFormPage;