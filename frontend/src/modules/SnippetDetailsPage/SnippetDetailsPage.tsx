import { useEffect, useState } from 'react';
import styles from './SnippetDetailsPage.module.scss';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { addFavorite, getById, removeFavorite } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';
import CodeEditor from '../../components/CodeEditor/CodeEditor';
import type { SnippetDetailsType } from '../../types/SnippetDetailsType';
import Tag from '../../components/Tag/Tag';
import toast, { type Toast } from 'react-hot-toast';
import CustomToast from '../../components/CustomToast/CustomToast';
import Heart from '../../components/Heart/Heart';
import { useSnippetContext } from '../../contexts/SnippetContext';

const initialSnippet: SnippetDetailsType = {
  title: "",
  language: "",
  is_private: false,
  content: "",
  description: "",
  tags: [],
  user_id: 0,
  uuid: "",
  created_at: "",
  updated_at: "",
};

const SnippetDetailsPage = () => {
  const [snippet, setSnippet] = useState<SnippetDetailsType>(initialSnippet);
  const { snippetId } = useParams();
  const { accessToken } = useAuthContext();
  const { favoriteSnippetsIds, setFavoriteSnippetsIds } = useSnippetContext();
  const navigate = useNavigate();

  const { mutate: getSnippet, isPending, isError } = useMutation({
    mutationFn: () => getById(snippetId ?? '', accessToken),
    onSuccess: (response) => setSnippet(response.data),
  });

  const { mutate: copyContent } = useMutation({
    mutationFn: () => navigator.clipboard.writeText(snippet.content),
    onSuccess: () => {
      toast.custom((t: Toast) => (
        <CustomToast
          t={t}
          title="Copied!"
          message="Code snippet has been copied to clipboard."
          type={'success'}
        />
      ), {
        duration: 1000,
      });
    },
    onError: () => {
      toast.custom((t: Toast) => (
        <CustomToast
          t={t}
          title="Failed to Copy"
          message="Could not copy the code snippet."
          type={'error'}
        />
      ), {
        duration: 1000,
      });
    }
  })

  useEffect(() => {
    getSnippet();
  }, [snippetId, accessToken]);

  if (isPending) {
    return (
      <main className={styles.main} aria-busy="true" aria-live="polite">
        <Loader />
      </main>
    );
  }

  if (isError) {
    return (
      <main className={styles.main} aria-live="assertive">
        <div className={styles.error} role="alert">Failed to load snippet details.</div>
      </main>
    );
  }

  function handleHeartClick(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();
    event.stopPropagation();

    if (favoriteSnippetsIds.includes(snippet.uuid)) {
      removeFavorite(accessToken, snippet.uuid);
      setFavoriteSnippetsIds(prev => prev.filter(id => id !== snippet.uuid));
    } else {
      addFavorite(accessToken, snippet.uuid);
      setFavoriteSnippetsIds(prev => [...prev, snippet.uuid]);
    }
  }

  return (
    <main className={styles.main}>
      <div className={styles.head}>
        <h2 className={styles.title} id="snippet-title">{snippet.title || "Untitled"}</h2>

        <div className={styles.buttons} role="group" aria-label="Snippet actions">
          <button className={styles.buttonsHeart} onClick={handleHeartClick}>
            <Heart isFilled={favoriteSnippetsIds.includes(snippet.uuid)} />
          </button>
          <button
            className={`${styles.buttonsItem} ${styles.copy}`}
            onClick={() => copyContent()}
            aria-label="Copy code snippet to clipboard"
            type="button"
          >
            Copy Code
          </button>
          <button
            onClick={() => navigate(`/snippets/edit/${snippetId}`)}
            className={styles.buttonsItem}
            aria-label="Edit this code snippet"
            type="button"
          >
            Edit
          </button>
        </div>
      </div>

      <div className={styles.line} aria-hidden="true" />

      <div className={styles.content}>
        <CodeEditor
          language={snippet.language}
          value={snippet.content}
          readonly={true}
          aria-label={snippet.title ? `Code for ${snippet.title}` : 'Code snippet'}
        />
      </div>

      <div className={styles.details} aria-label="Snippet information">
        <h3 className={styles.detailsTitle} id="snippet-info-heading">Snippet Information</h3>
        <div className={styles.line} aria-hidden="true" />

        <div className={styles.detailsInfo}>
          <div className={styles.container} role="list" aria-label="Snippet attributes">
            <span className={styles.containerItem}>
              <strong className={`${styles.type} ${styles.key}`}>Language:</strong>
              <span className={styles.value} aria-label="Snippet language">{snippet.language ? snippet.language : 'Unknown'}</span>
            </span>
            <span className={styles.containerItem}>
              <strong className={`${styles.key} ${styles.type}`}>Created:</strong>
              <span className={styles.value} aria-label="Created date">
                {snippet.created_at ? new Date(snippet.created_at).toLocaleString() : 'N/A'}
              </span>
            </span>
            <span className={styles.containerItem}>
              <strong className={`${styles.type} ${styles.key}`}>Visibility:</strong>
              <span className={styles.value} aria-label="Visibility">
                {typeof snippet.is_private === "boolean"
                  ? snippet.is_private ? "Private" : "Public"
                  : "Unknown"}
              </span>
            </span>
            <span className={styles.containerItem}>
              <strong className={`${styles.key} ${styles.type}`}>Last updated:</strong>
              <span className={styles.value} aria-label="Last updated">
                {snippet.updated_at ? new Date(snippet.updated_at).toLocaleString() : 'N/A'}
              </span>
            </span>
          </div>

          {snippet.description && snippet.description.length > 0 && (
            <div className={styles.detailsItem}>
              <strong className={styles.key} id="snippet-description-label">Description</strong>
              <p className={`${styles.text} ${styles.value}`} aria-labelledby="snippet-description-label">{snippet.description}</p>
            </div>
          )}

          {Array.isArray(snippet.tags) && snippet.tags.length > 0 && (
            <div className={styles.detailsItem}>
              <strong id="snippet-tags-label">Tags</strong>
              <div className={styles.tags} role="list" aria-labelledby="snippet-tags-label">
                {snippet.tags.map((tag, i) => (
                  <Tag key={tag + i} content={tag} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
};

export default SnippetDetailsPage;