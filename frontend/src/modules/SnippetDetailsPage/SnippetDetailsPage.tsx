import { useEffect, useState } from 'react';
import styles from './SnippetDetailsPage.module.scss';
import { useParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { getById } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';
import CodeEditor from '../../components/CodeEditor/CodeEditor';
import type { SnippetDetailsType } from '../../types/SnippetDetailsType';
import Tag from '../../components/Tag/Tag';
import toast, { type Toast } from 'react-hot-toast';
import CustomToast from '../../components/CustomAuthToast/CustomToast';

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

  const { mutate: getSnippet, isPending, isError } = useMutation({
    mutationFn: () => getById(snippetId ?? '', accessToken),
    onSuccess: (response) => setSnippet(response.data),
    onError: () => { },
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
        duration: 2500,
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
        duration: 2500,
      });
    }
  })

  useEffect(() => {
    getSnippet();
  }, [snippetId, accessToken]);

  if (isPending) {
    return (
      <main className={styles.main}>
        <Loader />
      </main>
    );
  }

  if (isError) {
    return (
      <main className={styles.main}>
        <div className={styles.error}>Failed to load snippet details.</div>
      </main>
    );
  }

  return (
    <main className={styles.main}>
      <div className={styles.head}>
        <h2 className={styles.title}>{snippet.title || "Untitled"}</h2>

        
      </div>

      <div className={styles.line} />

      <div className={styles.content}>
        <CodeEditor
          language={snippet.language}
          value={snippet.content}
          readonly={true}
        />
      </div>

      <div className={styles.details}>
        <h3 className={styles.detailsTitle}>Snippet Information</h3>
        <div className={styles.line} />

        <div className={styles.detailsInfo}>
          <div className={styles.container}>
            <span className={styles.containerItem}>
              <strong className={styles.type}>Language:</strong>
              {snippet.language ? snippet.language : 'Unknown'}
            </span>
            <span className={styles.containerItem}>
              <strong className={styles.type}>Visibility:</strong>
              {typeof snippet.is_private === "boolean"
                ? snippet.is_private ? "Private" : "Public"
                : "Unknown"}
            </span>
          </div>

          {snippet.description && snippet.description.length > 0 && (
            <div className={styles.detailsIteml}>
              <strong className={styles.type}>Description:</strong>
              <p className={styles.text}>{snippet.description}</p>
            </div>
          )}

          {Array.isArray(snippet.tags) && snippet.tags.length > 0 && (
            <div className={styles.detailsItem}>
              <strong className={styles.type}>Tags:</strong>
              <div className={styles.tags}>
                {snippet.tags.map(tag => (
                  <Tag content={tag} />
                ))}
              </div>
            </div>
          )}

          <div className={styles.container}>
            <span className={styles.containerItem}>
              <strong className={styles.type}>Created:</strong>
              {snippet.created_at ? new Date(snippet.created_at).toLocaleString() : 'N/A'}
            </span>

            <span className={styles.containerItem}>
              <strong className={styles.type}>Last updated:</strong>
              {snippet.updated_at ? new Date(snippet.updated_at).toLocaleString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>
    </main>
  );
};

export default SnippetDetailsPage;