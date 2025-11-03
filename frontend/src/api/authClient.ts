import axios from 'axios';
import type { AxiosResponse } from 'axios';
import type { AccessToken } from '../types/Tokens';

const SERVER_BASE_URL = import.meta.env.VITE_SERVER_BASE_URL;

export const authClient = axios.create({
  baseURL: `${SERVER_BASE_URL}/api/v1/auth`,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

export const register = (username: string, email: string, password: string) => {
  return authClient.post('/register', {
    username,
    email,
    password,
  })
}

export const activate = (activation_token: string | undefined) => {
  return authClient.post('/activate', { activation_token });
}

type LoginType = {
  access_token: string;
}

export const login = (
  login: string,
  password: string
): Promise<AxiosResponse<LoginType>> => {
  return authClient.post<LoginType>('/login', { login, password });
}

type RefreshResponse = {
  access_token: string;
};

export const refresh = (): Promise<AxiosResponse<RefreshResponse>> => {
  return authClient.post<RefreshResponse>('/refresh');
};

export const resetRequest = (email: string) => {
  return authClient.post('/reset-password/request', { email });
}

export const resetComplete = (
  password: string,
  email: string,
  password_reset_token: string | undefined
) => {
  return authClient.post('/reset-password/complete', { password, email, password_reset_token });
}

export const changePassword = (
  old_password: string,
  new_password: string,
  token: AccessToken
) => {
  return authClient.post('/change-password', {
    old_password,
    new_password
  }, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}