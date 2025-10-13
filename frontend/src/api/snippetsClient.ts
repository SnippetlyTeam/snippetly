import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { SnippetType } from '../types/SnippetType';
import type { NewSnippetType } from '../types/NewSnippetType';
import type { SnippetDetailsType } from '../types/SnippetDetailsType';

const SERVER_BASE_URL: string = import.meta.env.VITE_SERVER_BASE_URL as string;

export const snippetsClient: AxiosInstance = axios.create({
  baseURL: `${SERVER_BASE_URL}/api/v1/snippets`,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const getAll = (
  token: string,
  params: { page?: number; per_page?: number; language?: string; is_private?: boolean; tags?: string[] } = {}
): Promise<AxiosResponse> => {
  return snippetsClient.get(
    '/',
    {
      headers: { 'Authorization': `Bearer ${token}` },
      params
    }
  );
};

export const getById = (uuid: string, token: string | undefined): Promise<AxiosResponse<SnippetDetailsType>> => {
  return snippetsClient.get<SnippetDetailsType>(
    `/${uuid}`,
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
};

export const create = (snippet: NewSnippetType, token: string | undefined): Promise<AxiosResponse<SnippetType>> => {
  return snippetsClient.post(
    '/create',
    snippet,
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
};

export const update = (
  uuid: string,
  snippet: Partial<NewSnippetType>,
  token: string | undefined,
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