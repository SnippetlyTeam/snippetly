import { Link } from 'react-router-dom';
import styles from './ProfilePage.module.scss';

const Settings = () => {
  return (
    <div className={styles.settings}>
      <h3 className={styles.settingsTitle}>Account Settings</h3>

      <div className={styles.settingsItem}>
        <span>Profile Visibility</span>

        <select className={styles.select} defaultValue="public" aria-label="Profile visibility">
          <option value="public">Public</option>
          <option value="private">Private</option>
        </select>
      </div>
      <div className={styles.settingsItem}>
        <span>Change Password</span>
        <Link to='' className={styles.link}>Update Password</Link>
      </div>
    </div>
  )
}

export default Settings;