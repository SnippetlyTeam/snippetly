import { useMutation } from '@tanstack/react-query';
import styles from './ProfilePage.module.scss';
import { getProfile } from '../../api/profileClient';
import { useAuthContext } from '../../contexts/AuthContext';

const ProfilePage = () => {
  const { accessToken } = useAuthContext();

  const { mutate } = useMutation({
    mutationFn: () => getProfile(accessToken),
  });

  return (
    <main className={styles.main}>
      <div className={styles.head}>
        <div className={styles.userInfo}>
          <h3></h3>
        </div>
        <div className={styles.navigation}></div>
      </div>

      <div className={styles.profileDetails}></div>
      <div className={styles.statistics}></div>
    </main>
  );
}

export default ProfilePage;