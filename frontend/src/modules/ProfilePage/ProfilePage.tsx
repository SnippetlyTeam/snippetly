import { useMutation } from '@tanstack/react-query';
import styles from './ProfilePage.module.scss';
import { getProfile } from '../../api/profileClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useEffect, useState } from 'react';
import type { ProfileType } from '../../types/ProfileType';
import { Loader } from '../../components/Loader';

const ProfilePage = () => {
  const { accessToken } = useAuthContext();
  const emptyProfile: ProfileType = {
    first_name: "",
    last_name: "",
    gender: "male",
    date_of_birth: "",
    info: "",
    id: 0,
    user_id: 0,
    avatar_url: "",
  };
  const [profile, setProfile] = useState<ProfileType>(emptyProfile);

  const { mutate: loadProfile, isPending } = useMutation({
    mutationFn: () => getProfile(accessToken),
    onSuccess: (response) => setProfile(response.data),
  });

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  return (
    <main className={styles.main}>
      {isPending ? <Loader /> : (
        <>
          <div className={styles.head}>
            <div className={styles.userInfo}>
              <h3>{profile.user_id}</h3>
            </div>
            <div className={styles.navigation}></div>
          </div>

          <div className={styles.profileDetails}></div>
          <div className={styles.statistics}></div>
        </>
      )}
    </main>
  );
}

export default ProfilePage;