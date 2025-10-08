import axios from 'axios';
import type { AxiosResponse } from 'axios';

const SERVER_BASE_URL = import.meta.env.VITE_SERVER_BASE_URL;

export const authClient = axios.create({
  baseURL: `${SERVER_BASE_URL}/api/v1/auth`,
  headers: { 'Content-Type': 'application/json' }
})

export const register = (password: string, username: string, email: string) => {
  return authClient.post('/register', {
    password,
    username,
    email,
  })
}

export const activate = (activation_token: string | undefined) => {
  return authClient.post('/activate', { activation_token });
}

type LoginType = {
  access_token: string;
  refresh_token: string
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

export const refresh = (
  refresh_token: string
): Promise<AxiosResponse<RefreshResponse>> => {
  return authClient.post<RefreshResponse>('/refresh', { refresh_token });
};

export const resetRequest = (email: string) => {
  return authClient.post('/reset-password/request', { email });
}

export const resetComplete = (
  password: string,
  email: string,
  token: string | undefined
) => {
  return authClient.post('/reset-password/complete', { password, email, token });
}
