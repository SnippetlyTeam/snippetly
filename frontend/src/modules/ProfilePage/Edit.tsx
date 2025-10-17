import { useOutletContext } from 'react-router-dom';
import styles from './Edit.module.scss';
import type { ProfileType } from '../../types/ProfileType';
import { useRef, useState } from 'react';
import { useOnClickOutside } from '../shared/hooks/useOnClickOutside';

const Edit = () => {
  const { profile } = useOutletContext<{ profile: ProfileType }>();
  const [isGenderDropdownOpen, setIsGenderDropdownOpen] = useState(false);
  const genderDropdownRef = useRef<HTMLDivElement>(null);

  useOnClickOutside(genderDropdownRef as React.RefObject<HTMLElement>, () => setIsGenderDropdownOpen(false));

  return (
    <div className={styles.edit}>
      <h3 className={styles.editTitle}>Edit Personal Information</h3>

      <form className={styles.form}>
        <div className={styles.formItem}>
          <label htmlFor="">First Name</label>
          <input type="text" />
        </div>

        <div className={styles.formItem}>
          <label htmlFor="">Last Name</label>
          <input type="text" />
        </div>

        <div className={styles.formItem}>
          <label htmlFor="">Date of Birth</label>
          <input type="date" />
        </div>

        <div className={styles.formItem}>
          <label htmlFor="gender">Gender</label>

          <div className="dropdown" ref={genderDropdownRef}>
            <button
              type="button"
              className="dropdownTrigger"
              onClick={() => setIsGenderDropdownOpen(prev => !prev)}
            >
              Gender
            </button>
            {isGenderDropdownOpen && (
              <div className="dropdownMenu">
                <button className="dropdownItem" type="button" value="male">Male</button>
                <button className="dropdownItem" type="button" value="female">Female</button>
                <button className="dropdownItem" type="button" value="other">Other</button>
                <button className="dropdownItem" type="button" value="prefer_not_to_say">Prefer not to say</button>
              </div>
            )}
          </div>
        </div>

        <div className={`${styles.formItem} ${styles.bio}`}>
          <label htmlFor="">Bio</label>
          <textarea className={styles.textarea} />
        </div>
      </form>

      <div className={styles.buttons}>
        <button className={styles.buttonsCancel}>Cancel</button>
        <button className={styles.buttonsSave}>Save</button>
      </div>
    </div>
  )
}

export default Edit;