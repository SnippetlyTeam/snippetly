import { useMutation } from '@tanstack/react-query';
import styles from './ProfilePage.module.scss';
import { getProfile } from '../../api/profileClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useEffect, useState } from 'react';
import type { ProfileType } from '../../types/ProfileType';
import { Loader } from '../../components/Loader';
import { useNavigate } from 'react-router-dom';

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
  const navigate = useNavigate();

  const { mutate: loadProfile, isPending } = useMutation({
    mutationFn: () => getProfile(accessToken),
    onSuccess: (response) => {
      console.log(response.data)
      setProfile(response.data);
    },
  });

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  return (
    <main className={styles.main}>
      {isPending ? <Loader /> : (
        <>
          <div className={styles.head}>
            <div className={styles.user}>
              <div className={styles.container}>
                <div className={styles.avatar}>
                  <img
                    src={profile.avatar_url}
                    alt=""
                    className={styles.avatarContent}
                  />
                </div>
                <div className={styles.userInfo}>
                  <h3 className={styles.name}>
                    {profile.first_name + ' '}
                    {profile.last_name}
                  </h3>
                  <span className={styles.username}>@{profile.user_id}</span>
                </div>
              </div>

              <button 
                className={styles.editButton}
                onClick={() => navigate('/profile/edit')}
              >Edit Profile</button>
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