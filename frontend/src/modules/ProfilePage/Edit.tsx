import { useNavigate, useOutletContext } from 'react-router-dom';
import styles from './Edit.module.scss';
import type { ProfileType } from '../../types/ProfileType';
import { useRef, useState } from 'react';
import { useOnClickOutside } from '../shared/hooks/useOnClickOutside';
import { updateProfile } from '../../api/profileClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader } from '../../components/Loader';
import toast from 'react-hot-toast';
import CustomToast from '../../components/CustomToast/CustomToast';

const GENDER_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
];

const GENDER_NOT_SPECIFIED_LABEL = 'Not specified';
function getGenderLabel(val: string | null | undefined) {
  if (!val) return GENDER_NOT_SPECIFIED_LABEL;
  const found = GENDER_OPTIONS.find(o => o.value === val);
  return found ? found.label : GENDER_NOT_SPECIFIED_LABEL;
}

const Edit = () => {
  const { profile } = useOutletContext<{ profile: ProfileType }>();
  const { accessToken } = useAuthContext();
  const [isGenderDropdownOpen, setIsGenderDropdownOpen] = useState(false);
  const genderDropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const formatDateForInput = (dateString?: string): string => {
    if (!dateString) return '';
    try {
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
        return dateString;
      }
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '';
      return date.toISOString().split('T')[0];
    } catch {
      return '';
    }
  };

  type EditableProfileFields = {
    first_name: string;
    last_name: string;
    date_of_birth: string;
    gender: string | null;
    info: string;
  };

  const initialData = useRef<EditableProfileFields>({
    first_name: profile.first_name ?? '',
    last_name: profile.last_name ?? '',
    date_of_birth: formatDateForInput(profile.date_of_birth),
    gender: typeof profile.gender === 'string' &&
      (profile.gender === 'male' || profile.gender === 'female' || profile.gender === 'other' || profile.gender === 'prefer_not_to_say')
      ? profile.gender
      : null,
    info: profile.info ?? '',
  });

  const [formData, setFormData] = useState<EditableProfileFields>(initialData.current);
  const [errors, setErrors] = useState<Partial<Record<keyof EditableProfileFields, string>>>({});
  const [isChanged, setIsChanged] = useState(false);

  function handleFormDataChange(key: keyof typeof formData, value: string) {
    const updatedFormData = { ...formData, [key]: value };

    const isAllEqual = Object.entries(initialData.current).every(
      ([k, v]) => {
        const currentValue = updatedFormData[k as keyof typeof updatedFormData];

        if (k === 'gender') {
          const isCurrentNotSpecified = !currentValue || currentValue === 'other' || currentValue === 'prefer_not_to_say';
          const isInitialNotSpecified = !v || v === 'other' || v === 'prefer_not_to_say';
          return isCurrentNotSpecified === isInitialNotSpecified;
        }

        if (k === 'first_name' || k === 'last_name' || k === 'info') {
          return (currentValue?.toString().trim() || '') === (v?.toString().trim() || '');
        }
        return currentValue === v;
      }
    );

    setIsChanged(!isAllEqual);

    setFormData(prev => ({
      ...prev,
      [key]: value,
    }));

    if (errors[key]) {
      setErrors(prev => ({ ...prev, [key]: undefined }));
    }
  }

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof EditableProfileFields, string>> = {};
    let isValid = true;

    if (formData.first_name.length > 50) {
      newErrors.first_name = 'First Name must not exceed 50 characters.';
      isValid = false;
    }

    if (formData.last_name.length > 50) {
      newErrors.last_name = 'Last Name must not exceed 50 characters.';
      isValid = false;
    }

    if (formData.info.length > 250) {
      newErrors.info = 'Bio must not exceed 250 characters.';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  function handleGenderChange(value: string) {
    handleFormDataChange('gender', value);
    setIsGenderDropdownOpen(false);
  }

  const { mutate, isPending } = useMutation({
    mutationFn: () => {
      const changedFields = Object.fromEntries(
        Object.entries(formData).filter(
          ([key, value]) => initialData.current[key as keyof EditableProfileFields] !== value
        ).map(([key, value]) => {
          if (key === 'gender') {
            if (value === 'male' || value === 'female') {
              return [key, value];
            } else {
              return [key, null];
            }
          }
          const trimmedValue =
            key === 'first_name' || key === 'last_name' || key === 'info'
              ? value?.toString().trim()
              : value;
          return [key, trimmedValue];
        })
      );
      return updateProfile(accessToken, changedFields);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', profile.username, accessToken] });
      queryClient.invalidateQueries({ queryKey: ['myProfile', accessToken] });

      navigate(`/profile/${profile.username}`, {
        state: {
          title: 'Profile Updated',
          message: 'Your profile has been updated successfully.',
          type: 'success'
        }
      });
    },
    onError: (error) => {
      console.error('Error updating profile:', error);
      toast.custom(t => (
        <CustomToast
          t={t}
          title="Update Failed"
          message="There was an error updating your profile. Please try again."
          type="error"
        />
      ), {
        duration: 2500,
      });
    }
  });

  function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (validate()) {
      mutate();
    }
  }

  useOnClickOutside(genderDropdownRef as React.RefObject<HTMLElement>, () => setIsGenderDropdownOpen(false));

  return (
    <div className={styles.edit}>
      <h3 className={styles.editTitle}>Edit Personal Information</h3>

      <form className={styles.form} onSubmit={handleFormSubmit}>
        <div className={styles.formItem}>
          <label htmlFor="">First Name</label>
          <input
            type="text"
            value={formData.first_name}
            onChange={event => handleFormDataChange('first_name', event.target.value)}
          />
          {errors.first_name && <span className={styles.error}>{errors.first_name}</span>}
        </div>

        <div className={styles.formItem}>
          <label htmlFor="">Last Name</label>
          <input
            type="text"
            value={formData.last_name}
            onChange={event => handleFormDataChange('last_name', event.target.value)}
          />
          {errors.last_name && <span className={styles.error}>{errors.last_name}</span>}
        </div>

        <div className={styles.formItem}>
          <label htmlFor="">Date of Birth</label>
          <input
            type="date"
            value={formData.date_of_birth}
            onChange={event => handleFormDataChange('date_of_birth', event.target.value)}
          />
        </div>

        <div className={styles.formItem}>
          <label htmlFor="gender">Gender</label>
          <div className="dropdown" ref={genderDropdownRef}>
            <button
              type="button"
              className="dropdownTrigger"
              onClick={() => setIsGenderDropdownOpen(prev => !prev)}
            >
              {getGenderLabel(formData.gender)}
            </button>
            {isGenderDropdownOpen && (
              <div className="dropdownMenu">
                {GENDER_OPTIONS.map(option => (
                  <button
                    key={option.value}
                    className="dropdownItem"
                    type="button"
                    value={option.value}
                    onClick={() => handleGenderChange(option.value)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className={`${styles.formItem} ${styles.bio}`}>
          <label htmlFor="">Bio</label>
          <textarea
            className={styles.textarea}
            value={formData.info}
            onChange={event => handleFormDataChange('info', event.target.value)}
          />
          {errors.info && <span className={styles.error}>{errors.info}</span>}
        </div>

        <div className={styles.buttons}>
          <button
            type="button"
            className={styles.buttonsCancel}
            onClick={() => navigate(`/profile/${profile.username}`)}
          >Cancel</button>

          <button
            type='submit'
            className={styles.buttonsSave}
            disabled={isPending || !isChanged}
          >
            {isPending ? <Loader buttonContent /> : 'Save'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default Edit;