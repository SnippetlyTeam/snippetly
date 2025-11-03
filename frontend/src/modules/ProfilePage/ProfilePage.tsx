import { useQuery } from '@tanstack/react-query';
import styles from './ProfilePage.module.scss';
import { getProfile, getProfileByUsername } from '../../api/profileClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';
import { NavLink, useNavigate, Outlet, useParams, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import CustomToast from '../../components/CustomToast/CustomToast';
import { toast, type Toast } from 'react-hot-toast';
import { logout } from '../../api/authClient';
import { flushSync } from 'react-dom';

const ProfilePage = () => {
  const { accessToken, setAccessToken } = useAuthContext();
  const navigate = useNavigate();
  const location = useLocation();
  const { username } = useParams();

  const { data: myProfile } = useQuery({
    queryKey: ['myProfile', accessToken],
    queryFn: () => getProfile(accessToken).then(res => res.data),
    enabled: !!accessToken,
  });

  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ['profile', username, accessToken],
    queryFn: () => {
      if (username) {
        return getProfileByUsername(username, accessToken).then(res => res.data);
      }
      return getProfile(accessToken).then(res => res.data);
    },
    enabled: !!accessToken,
  });

  const isMyProfile =
    !!myProfile && !!profile && myProfile.username === profile.username;

  useEffect(() => {
    if (
      location.state &&
      (location.state.title || location.state.message || location.state.type)
    ) {
      const { title = '', message = '', type = 'success' } = location.state || {};

      toast.custom((t: Toast) => (
        <CustomToast
          t={t}
          title={title}
          message={message}
          type={type}
        />
      ), {
        duration: 2500,
      });

      navigate(location.pathname, { replace: true, state: null });
    }
  }, [location, navigate]);

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
                  src={profile.avatar_url || '/'}
                  alt="Avatar Image"
                  className={styles.avatarContent}
                  referrerPolicy="no-referrer"
                  onError={e => {
                    const target = e.currentTarget as HTMLImageElement;
                    const fallback = `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(profile.username)}`;
                    if (target.src !== fallback) {
                      target.src = fallback;
                    }
                  }}
                />
              </div>
              <div className={styles.userInfo}>
                <h3 className={styles.name}>
                  {profile.first_name + ' '}
                  {profile.last_name}
                </h3>
                <span className={styles.username}>@{profile.username}</span>
              </div>
            </div>

            {(isMyProfile && !location.pathname.includes('/edit')) && (
              <div className={styles.editButtons}>
                <button
                  className={`${styles.editButtonsButton} ${styles.editButtonsLogout}`}
                  onClick={() => logout(accessToken).then(() => {
                    flushSync(() => setAccessToken(undefined));
                    navigate('/sign-in', {
                      replace: true,
                      state: {
                        title: 'Logged Out',
                        message: 'You have been logged out successfully.',
                        type: 'success',
                      }
                    });
                  })}
                >Log out</button>
                <button
                  className={styles.editButtonsButton}
                  onClick={() => navigate(`/profile/${profile.username}/edit`)}
                >Edit Profile</button>
              </div>
            )}
          </div>
          <nav className={styles.nav} aria-label="Profile sections">
            <ul className={styles.navList} role="tablist">
              <li className={styles.navItem}>
                <NavLink
                  to={`/profile/${profile.username}`}
                  className={({ isActive }) => `
                    ${styles.navLink} 
                    ${isActive || location.pathname.includes('/edit')
                      ? styles.navLinkActive
                      : ''
                    }
                  `}
                  end
                >
                  Overview
                </NavLink>
              </li>
              <li className={styles.navItem}>
                <NavLink
                  to={`/profile/${profile.username}/snippets`}
                  className={({ isActive }) => `
                    ${styles.navLink} 
                    ${isActive ? styles.navLinkActive : ''}
                  `}
                >
                  Snippets
                </NavLink>
              </li>
              {isMyProfile && (
                <li className={styles.navItem}>
                  <NavLink
                    to={`/profile/${profile.username}/settings`}
                    className={({ isActive }) => `
                      ${styles.navLink} 
                      ${isActive ? styles.navLinkActive : ''}
                    `}
                  >
                    Settings
                  </NavLink>
                </li>
              )}
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