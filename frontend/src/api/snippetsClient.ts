import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { SnippetType } from '../types/SnippetType';
import type { NewSnippetType } from '../types/NewSnippetType';
import type { SnippetDetailsType } from '../types/SnippetDetailsType';
import type { AccessToken } from '../types/Tokens';
import type { FiltersType } from '../types/FiltersType';
import type { SnippetListResponse } from '../types/SnippetListResponse';

const SERVER_BASE_URL: string = import.meta.env.VITE_SERVER_BASE_URL as string;

export const snippetsClient: AxiosInstance = axios.create({
  baseURL: `${SERVER_BASE_URL}/api/v1/snippets`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export const getAll = (
  token: AccessToken,
  params: FiltersType = {}
): Promise<AxiosResponse<SnippetListResponse>> => {
  const { tags, ...otherParams } = params;
  const searchParams = new URLSearchParams();
  Object.entries(otherParams).forEach(([key, value]) => {
    if (value !== undefined) {
      searchParams.append(key, String(value));
    }
  });
  if (tags && Array.isArray(tags)) {
    tags.forEach(tag => {
      searchParams.append('tags', tag);
    });
  }

  return snippetsClient.get<SnippetListResponse>(
    `/?${searchParams.toString()}`,
    {
      headers: { 'Authorization': `Bearer ${token}` },
    }
  );
};

export const getFavorites = (token: AccessToken) => {
  return snippetsClient.get<SnippetListResponse>(
    '/favorites/',
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
}

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

export const addFavorite = (token: AccessToken, uuid: string) => {
  return snippetsClient.post(
    '/favorites/',
    { uuid },
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

export const removeFavorite = (token: AccessToken, uuid: string) => {
  return snippetsClient.delete(
    `/favorites/${uuid}`,
    { headers: { 'Authorization': `Bearer ${token}` } },
  )
};

export const search = (token: AccessToken, query: string) => {
  return snippetsClient.get(
    `/search/${query}`,
    { headers: { 'Authorization': `Bearer ${token}` } },
  )
}