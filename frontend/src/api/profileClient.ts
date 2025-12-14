import axios from 'axios';
import type { AxiosResponse } from 'axios';
import type { ProfileType } from '../types/ProfileType';
import type { AccessToken } from '../types/Tokens';

const SERVER_BASE_URL: string = import.meta.env.VITE_SERVER_BASE_URL || '';

export const profileClient = axios.create({
  baseURL: `${SERVER_BASE_URL}/api/v1/profile`,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

export const getProfile = (token: AccessToken): Promise<AxiosResponse<ProfileType>> => {
  return profileClient.get<ProfileType>('/', {
    headers: { Authorization: `Bearer ${token}` },
  });
};

export const getProfileByUsername = (username: string, token: AccessToken): Promise<AxiosResponse<ProfileType>> => {
  return profileClient.get<ProfileType>(`/${username}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

export const updateProfile = (
  token: AccessToken,
  profile: Partial<ProfileType>
): Promise<AxiosResponse<ProfileType>> => {
  return profileClient.patch<ProfileType>(
    '/',
    profile,
    { headers: { Authorization: `Bearer ${token}` } }
  );
};

export const setAvatar = (
  token: AccessToken,
  avatarFile: File
): Promise<AxiosResponse<ProfileType>> => {
  const formData = new FormData();
  formData.append('avatar', avatarFile);
  return profileClient.post<ProfileType>(
    '/avatar',
    formData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    }
  );
};

export const removeAvatar = () => {
  return profileClient.delete('');
}