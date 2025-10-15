import { useQuery } from '@tanstack/react-query';
import styles from './ProfilePage.module.scss';
import { getProfile } from '../../api/profileClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';
import { NavLink, useNavigate, Outlet } from 'react-router-dom';

const ProfilePage = () => {
  const { accessToken } = useAuthContext();
  const navigate = useNavigate();

  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ['profile', accessToken],
    queryFn: () => getProfile(accessToken).then(res => res.data),
    enabled: !!accessToken,
  });

  if (isError) {
    return <div>Error loading profile.</div>;
  }
  if (isLoading || !profile) {
    return <Loader />;
  }

  return (
    <main className={styles.main}>
      <div className={styles.mainContent}>
        <div className={styles.head}>
          <div className={styles.user}>
            <div className={styles.container}>
              <div className={styles.avatar}>
                <img
                  src={profile.avatar_url}
                  alt="Avatar Image"
                  className={styles.avatarContent}
                />
              </div>
              <div className={styles.userInfo}>
                <h3 className={styles.name}>
                  {profile.first_name + ' '}
                  {profile.last_name}
                </h3>
                {/* Невелике виправлення: user_id краще брати з об'єкта user, якщо він є */}
                <span className={styles.username}>@{profile.user_id}</span>
              </div>
            </div>

            <button
              className={styles.editButton}
              onClick={() => navigate('/profile/edit')}
            >Edit Profile</button>
          </div>
          <nav className={styles.nav} aria-label="Profile sections">
            <ul className={styles.navList} role="tablist">
              <li className={styles.navItem}>
                <NavLink
                  to="/profile"
                  className={({ isActive }) => `
                    ${styles.navLink} 
                    ${isActive ? styles.navLinkActive : ''}
                  `}
                  end
                >
                  Overview
                </NavLink>
              </li>
              <li className={styles.navItem}>
                <NavLink
                  to="/profile/snippets"
                  className={({ isActive }) => `
                    ${styles.navLink} 
                    ${isActive ? styles.navLinkActive : ''}
                  `}
                >
                  Snippets
                </NavLink>
              </li>
              <li className={styles.navItem}>
                <NavLink
                  to="/profile/settings"
                  className={({ isActive }) => `
                    ${styles.navLink} 
                    ${isActive ? styles.navLinkActive : ''}
                  `}
                >
                  Settings
                </NavLink>
              </li>
            </ul>
          </nav>
        </div>
        <div className={styles.profile}>
          <Outlet context={{ profile }} />
        </div>
      </div>
    </main>
  );
}

export default ProfilePage;