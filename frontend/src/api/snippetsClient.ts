import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { SnippetType } from '../types/SnippetType';
import type { NewSnippetType } from '../types/NewSnippetType';

const SERVER_BASE_URL: string = import.meta.env.VITE_SERVER_BASE_URL as string;

export const snippetsClient: AxiosInstance = axios.create({
  baseURL: `${SERVER_BASE_URL}/api/v1/snippets`,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const getAll = (token: string): Promise<AxiosResponse> => {
  return snippetsClient.get<SnippetType[]>(
    '/',
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
};

export const getById = (uuid: string, token: string): Promise<AxiosResponse<SnippetType>> => {
  return snippetsClient.get<SnippetType>(
    `/${uuid}`,
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
};

export const create = (snippet: NewSnippetType, token: string | null): Promise<AxiosResponse<SnippetType>> => {
  return snippetsClient.post(
    '/create',
    snippet,
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
};

export const update = (
  uuid: string,
  snippet: Partial<NewSnippetType>,
  token: string,
): Promise<AxiosResponse<SnippetType>> => {
  return snippetsClient.patch<SnippetType>(
    `/${uuid}`,
    snippet,
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
};

export const remove = (uuid: string, token: string): Promise<AxiosResponse<void>> => {
  return snippetsClient.delete<void>(
    `/${uuid}`,
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
};