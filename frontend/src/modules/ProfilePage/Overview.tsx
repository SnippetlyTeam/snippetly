import { useOutletContext } from 'react-router-dom';
import styles from './ProfilePage.module.scss';
import type { ProfileType } from '../../types/ProfileType';

type ProfileContextType = {
  profile: ProfileType,
}

const Overview = () => {
  const { profile } = useOutletContext<ProfileContextType>();

  return (
    <>
      <div className={styles.profileDetails}>
        <div className={styles.profileDetailsItem}>
          <h3 className={styles.profileDetailsTitle}>Your Biography</h3>
          <span>{profile.info}</span>
        </div>
        <div className={styles.profileDetailsItem}>
          <h3 className={styles.profileDetailsTitle}>Private Details</h3>
        </div>
      </div>
      <div className={styles.profileStatistics}>
        <h4 className={styles.profileStatisticsTitle}>Statistics</h4>
        <span className={styles.profileStatisticsContent}><strong>Snippets</strong></span>
        <span className={styles.profileStatisticsContent}><strong>Favorites</strong></span>
        <span className={styles.profileStatisticsContent}><strong>Public</strong></span>
        <span className={styles.profileStatisticsContent}><strong>Account Age</strong></span>
      </div>
    </>
  );
};

export default Overview;