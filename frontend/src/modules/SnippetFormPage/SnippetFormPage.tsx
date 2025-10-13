import { useEffect, useRef, useState } from 'react';
import styles from './SnippetFormPage.module.scss';
import CodeEditor from '../../components/CodeEditor/CodeEditor';
import MainButton from '../../components/MainButton/MainButton';
import { create, getById, update } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useNavigate, useParams } from 'react-router-dom';
import { Loader } from '../../components/Loader';
import { useOnClickOutside } from '../shared/hooks/useOnClickOutside';
import type { NewSnippetType } from '../../types/NewSnippetType';
import type { SnippetType } from '../../types/SnippetType';
import { useMutation } from '@tanstack/react-query';
import toast, { type Toast } from 'react-hot-toast';
import CustomToast from '../../components/CustomToast/CustomToast';
import CharacterCountIndicator from './CharacterCountIndicator';
import Tag from '../../components/Tag/Tag';

const SnippetFormPage = () => {
  const { snippetId } = useParams();
  const isEditMode = !!snippetId;
  const languages: string[] = ['JavaScript', 'Python'];

  const initialTitleRef = useRef<string>('');

  const [titleError, setTitleError] = useState('');
  const [contentError, setContentError] = useState('');
  const [tagsError, setTagsError] = useState('');

  const emptySnippet: NewSnippetType = {
    title: '',
    language: languages[0],
    is_private: false,
    content: '',
    description: '',
    tags: [],
  }

  const [isLanguageDropDownOpen, setIsLanguageDropdownOpen] = useState(false);
  const { accessToken } = useAuthContext();

  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const {
    mutate: createSnippet,
    isPending: isCreating,
  } = useMutation({
    mutationFn: (newSnippet: NewSnippetType) => create(newSnippet, accessToken),
    onSuccess: (response) => {
      console.log(response.data)
      setSnippet(emptySnippet);
      toast.custom((t: Toast) => (
        <CustomToast
          t={t}
          title="Snippet created successfully"
          message="Your snippet has been saved."
          type={'success'}
        />
      ), {
        duration: 2500,
      });
    },
    onError: (error) => {
      console.log(error)
    }
  });

  const {
    mutate: updateSnippet,
    isPending: isUpdating,
  } = useMutation({
    mutationFn: (newSnippet: NewSnippetType) => {
      return update(snippetId as string, newSnippet, accessToken)
    },
    onSuccess: () => {
      navigate('/snippets', {
        state: {
          title: 'Snippet updated successfully',
          message: 'Your snippet has been updated.',
          type: 'success'
        }
      });
    },
    onError: () => {
      navigate('/snippets', {
        state: {
          title: 'Update Failed',
          message: 'You can edit only your own snippets.',
          type: 'error'
        }
      });
    }
  });

  useOnClickOutside(dropdownRef as React.RefObject<HTMLElement>, () => {
    setIsLanguageDropdownOpen(false);
  });

  const [snippet, setSnippet] = useState<NewSnippetType | SnippetType>(emptySnippet);
  const [isLoading, setIsLoading] = useState(isEditMode);
  const [currentTag, setCurrentTag] = useState('');

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

  function validateForm() {
    let isValid = true;

    if (!snippet.title.trim() || snippet.title.trim().length < 3) {
      setTitleError('Please enter a title for your snippet');
      isValid = false;
    }

    if (!snippet.content.trim()) {
      setContentError('Snippet must contain code');
      isValid = false;
    }

    if (snippet.content.length > 50000) {
      setContentError('Snippet exceeds size limit of 10MB');
      isValid = false;
    }

    return isValid;
  }

  function isFormValid() {
    if (!snippet.title.trim() || snippet.title.trim().length < 3) {
      return false;
    }

    if (!snippet.content.trim()) {
      return false;
    }

    if (snippet.content.length > 50000) {
      return false;
    }

    return true
  }

  function handleAddTag(tagContent: string) {
    if (snippet.tags.length === 10) {
      setTagsError('You can add up to 10 tags only');
      return;
    }

    if (tagContent.length < 2) {
      setTagsError('Tag must be at least 2 characters');
      return;
    }

    if (!snippet.tags.includes(tagContent.trim())) {
      setSnippet(prev => ({
        ...prev,
        tags: [...prev.tags, tagContent]
      }));
    }

    setCurrentTag('');
  }

  function handleSnippetDetailsChange(key: keyof NewSnippetType, value: any) {
    switch (key) {
      case 'title':
        setTitleError('');
        break;
      case 'content':
        setContentError('');
        if (value.length > 50000) {
          setContentError('Snippet exceeds size limit of 10MB');
        }
        break;
      case 'language':
        setIsLanguageDropdownOpen(false);
        break;
      case 'tags':
        if (value.endsWith(',')) {
          handleAddTag(value.slice(0, -1));
        } else {
          setCurrentTag(value);
          setTagsError('');
        }
        return;
      default:
        break;
    }

    setSnippet(prev => ({
      ...prev,
      [key]: value,
    }));
  }

  async function handleSnippetSave(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!snippet) return;

    let isValid = validateForm();

    if (!isValid) return;

    if (isEditMode) {
      updateSnippet({
        title: snippet.title,
        language: snippet.language.toLowerCase(),
        is_private: snippet.is_private,
        content: snippet.content,
        description: snippet.description,
        tags: snippet.tags,
      });
      return;
    }

    createSnippet({
      title: snippet.title.trim(),
      language: snippet.language.toLowerCase(),
      is_private: snippet.is_private,
      content: snippet.content,
      description: snippet.description.trim(),
      tags: snippet.tags,
    });
  }

  useEffect(() => {
    if (isEditMode) {
      getById(snippetId, accessToken)
        .then(response => {
          if (response.status === 200) {
            setSnippet(response.data);
            initialTitleRef.current = response.data.title;
          }
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, []);

  return (
    <main className={styles.main}>
      <h2 id="snippet-form-heading">
        {isEditMode
          ? `Edit Snippet: ${initialTitleRef.current}`
          : 'Create a New Snippet'}
      </h2>
      {isLoading ? (
        <Loader />
      ) : (
        <>
          <form
            className={styles.form}
            noValidate
            onSubmit={handleSnippetSave}
            aria-labelledby="snippet-form-heading"
            autoComplete="off"
          >
            <div className={styles.formItem}>
              <label htmlFor="title">Title</label>
              <input
                className={styles.input}
                type="text"
                id="title"
                name="title"
                minLength={3}
                maxLength={100}
                placeholder="Enter snippet title"
                value={snippet.title}
                onChange={event => {
                  handleSnippetDetailsChange('title', event.target.value)
                }}
                required
                aria-required="true"
                aria-invalid={!!titleError}
                aria-describedby={titleError ? "title-error" : undefined}
                autoComplete="off"
              />

              {titleError && (
                <span className={styles.error} id="title-error" role="alert" aria-live="polite">{titleError}</span>
              )}

              <CharacterCountIndicator
                currentLength={snippet.title.length}
                maxLength={100}
              />
            </div>

            <div className={styles.formItem}>
              <label htmlFor="description">Description</label>
              <textarea
                name="description"
                id="description"
                placeholder="Describe what this code does..."
                value={snippet.description}
                className={styles.textarea}
                maxLength={500}
                onChange={event => {
                  handleSnippetDetailsChange('description', event.target.value);
                }}
                aria-describedby="description-hint"
                autoComplete="off"
              />

              <CharacterCountIndicator
                currentLength={snippet.description.length}
                maxLength={500}
              />
            </div>

            <div className={styles.container}>
              <div className={`${styles.formItem} ${styles.language}`}>
                <label id="language-label" htmlFor="language-dropdown-trigger">Language</label>
                <div ref={dropdownRef} className={styles.dropdown}>
                  <button
                    id="language-dropdown-trigger"
                    type="button"
                    className={`
                    ${styles.dropdownTrigger} 
                    ${isLanguageDropDownOpen ? styles.dropdownTriggerActive : ''}
                  `}
                    aria-haspopup="listbox"
                    aria-expanded={isLanguageDropDownOpen}
                    aria-labelledby="language-label language-dropdown-trigger"
                    onClick={() => setIsLanguageDropdownOpen(prev => !prev)}
                  >
                    {formatLanguage(snippet.language)}
                  </button>

                  {isLanguageDropDownOpen && (
                    <div
                      className={styles.dropdownMenu}
                      role="listbox"
                      aria-labelledby="language-label"
                      tabIndex={-1}
                    >
                      {languages.map(lang => (
                        <button
                          key={lang}
                          type="button"
                          name="language"
                          value={lang}
                          onClick={() => handleSnippetDetailsChange('language', lang)}
                          className={styles.dropdownItem}
                          role="option"
                          aria-selected={snippet.language === lang}
                          tabIndex={0}
                        >
                          {lang}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className={`${styles.formItem} ${styles.tag}`}>
                <label htmlFor="tags">Tags</label>
                <input
                  placeholder="e.g., react, hooks"
                  type="text"
                  id="tags"
                  name="tags"
                  autoComplete="off"
                  aria-describedby="tags-hint"
                  aria-disabled="true"
                  minLength={2}
                  maxLength={20}
                  value={currentTag}
                  onChange={event => handleSnippetDetailsChange('tags', event.target.value)}
                  onKeyDown={event => {
                    if (event.key === 'Enter') {
                      event.preventDefault();
                      if (currentTag.trim() !== '') {
                        handleSnippetDetailsChange('tags', currentTag + ',');
                      }
                    }
                  }}
                />
                <span className={styles.error}>{tagsError}</span>
                <div className={styles.tagsList}>
                  {snippet.tags.map(tag => (
                    <Tag
                      key={tag}
                      content={tag}
                      onClose={() => setSnippet(prev => ({
                        ...prev,
                        tags: [...prev.tags].filter(item => item !== tag),
                      }))}
                    />
                  ))}
                </div>
              </div>

              <div className={styles.formItem}>
                <label htmlFor="visibility">Visibility</label>
                <div className={styles.visibility}>
                  <input
                    type="checkbox"
                    id="visibility"
                    name="visibility"
                    checked={snippet.is_private}
                    onChange={() => handleSnippetDetailsChange('is_private', !snippet.is_private)}
                    className={styles.checkbox}
                    aria-checked={snippet.is_private}
                    aria-label={snippet.is_private ? "Private" : "Public"}
                  />
                  <span className={styles.visibilityState} id="visibility-state">
                    {snippet.is_private ? 'Private' : 'Public'}
                  </span>
                  <span className={styles.hint} id="visibility-hint">
                    {snippet.is_private
                      ? '(Only you can see)'
                      : '(Visible to everyone)'}
                  </span>
                </div>
              </div>
            </div>

            <div className={styles.formItem}>
              <label htmlFor="code-editor">Code</label>
              <CodeEditor
                value={snippet.content}
                onChange={(value) => handleSnippetDetailsChange('content', value)}
                language={formatLanguage(snippet.language)}
                aria-label="Code editor"
                aria-describedby={contentError ? "code-error" : undefined}
                aria-invalid={!!contentError}
              />
              <CharacterCountIndicator
                currentLength={snippet.content.length}
                maxLength={50000}
              />

              {contentError && (
                <span
                  className={styles.error}
                  id="code-error"
                  role="alert"
                  aria-live="polite"
                >{contentError}</span>
              )}
            </div>

            <MainButton
              content={(isCreating || isUpdating) ? <Loader buttonContent /> : 'Save Snippet'}
              type="submit"
              aria-label="Save Snippet"
              onClick={() => { }}
              disabled={!isFormValid()}
            />
          </form>
        </>
      )}
    </main>
  )
}

export default SnippetFormPage;