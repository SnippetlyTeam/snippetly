import { useOutletContext } from 'react-router-dom';
import styles from './ProfilePage.module.scss';
import type { ProfileType } from '../../types/ProfileType';
import { getAll } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useEffect, useState } from 'react';
import type { SnippetType } from '../../types/SnippetType';

type ProfileContextType = {
  profile: ProfileType,
}

const Overview = () => {
  const { profile } = useOutletContext<ProfileContextType>();

  const { accessToken } = useAuthContext();

  const [snippets, setSnippets] = useState<SnippetType[]>([]);

  useEffect(() => {
    getAll(accessToken, { username: profile.username })
      .then((response) => {
        setSnippets(response.data.snippets);
      })
  }, []);

  return (
    <>
      <div className={styles.profileDetails}>
        <div className={styles.profileDetailsItem}>
          <h3 className={styles.profileDetailsTitle}>Your Biography</h3>
          {profile.info && profile.info.trim().length > 0 ? (
            <span className={styles.profileDetailsContent}>{profile.info}</span>
          ) : (
            <span className={styles.profileDetailsContent}>No biography yet.</span>
          )}
        </div>
      </div>
      <div className={styles.profileStatistics}>
        <h4 className={styles.profileStatisticsTitle}>Statistics</h4>
        <span className={styles.profileStatisticsContent}><strong>Snippets: </strong>{snippets.length}</span>
        {snippets.length > 0 && (
          <span className={styles.profileStatisticsContent}>
            <strong>Public: </strong>
            {snippets.filter(item => !item.is_private).length}
          </span>
        )}
      </div>
    </>
  );
};

export default Overview;