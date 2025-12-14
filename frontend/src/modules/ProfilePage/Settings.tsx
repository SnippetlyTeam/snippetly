import { Link } from 'react-router-dom';
import styles from './ProfilePage.module.scss';

const Settings = () => (
  <div className={styles.settings}>
    <h3 className={styles.settingsTitle}>Account Settings</h3>
    <div className={styles.settingsItem}>
      <span>Change Password</span>
      <Link to={`/change-password`} className={styles.link}>Update Password</Link>
    </div>
  </div>
)

export default Settings;