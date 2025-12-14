import { useOutletContext } from 'react-router-dom';
import styles from './ProfilePage.module.scss';
import type { ProfileType } from '../../types/ProfileType';
import { getAll } from '../../api/snippetsClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useEffect, useState } from 'react';
import type { SnippetType } from '../../types/SnippetType';
import { useSnippetContext } from '../../contexts/SnippetContext';

type ProfileContextType = {
  profile: ProfileType,
}

const Overview = () => {
  const { profile } = useOutletContext<ProfileContextType>();

  const { accessToken } = useAuthContext();
  const { favoriteSnippetsIds } = useSnippetContext();

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
        <div className={styles.profileDetailsItem}>
          <h3 className={styles.profileDetailsTitle}>Personal Details</h3>
          <span className={styles.profileDetailsContent}>
            <strong>Age: </strong>
            {profile.date_of_birth
              ? (() => {
                const birthDate = new Date(profile.date_of_birth);
                const today = new Date();
                let age = today.getFullYear() - birthDate.getFullYear();
                const m = today.getMonth() - birthDate.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                  age--;
                }
                return age;
              })()
              : 'Not provided'}
          </span>
          <span className={styles.profileDetailsContent}>
            <strong>Gender: </strong>
            {profile.gender
              ? profile.gender.charAt(0).toUpperCase() + profile.gender.slice(1)
              : 'Not provided'}
          </span>
        </div>
      </div>
      <div className={styles.profileStatistics}>
        <h4 className={styles.profileStatisticsTitle}>Statistics</h4>
        <span className={styles.profileStatisticsContent}>
          <strong>Snippets: </strong>{snippets.length}
        </span>
        <span className={styles.profileStatisticsContent}>
          <strong>Public: </strong>
          {snippets.filter(item => !item.is_private).length}
        </span>
        <span className={styles.profileStatisticsContent}>
          <strong>Favorites: </strong>
          {favoriteSnippetsIds.length}
        </span>
      </div>
    </>
  );
};

export default Overview;