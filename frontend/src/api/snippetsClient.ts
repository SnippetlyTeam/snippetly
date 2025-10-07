import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { SnippetType } from '../types/SnippetType';

const SERVER_BASE_URL: string = import.meta.env.VITE_SERVER_BASE_URL as string;

export const snippetsClient: AxiosInstance = axios.create({
  baseURL: `${SERVER_BASE_URL}/api/v1/snippets`,
  headers: { 'Content-Type': 'application/json' }
});

export const getAll = (): Promise<AxiosResponse<SnippetType[]>> => {
  return snippetsClient.get<SnippetType[]>('/');
};

export const getById = (uuid: string): Promise<AxiosResponse<SnippetType>> => {
  return snippetsClient.get<SnippetType>(`/${uuid}`);
};

export const create = (snippet: SnippetType): Promise<AxiosResponse<SnippetType>> => {
  return snippetsClient.post<SnippetType>('/create', snippet);
};

export const update = (
  uuid: string,
  snippet: Partial<SnippetType>
): Promise<AxiosResponse<SnippetType>> => {
  return snippetsClient.patch<SnippetType>(`/${uuid}`, snippet);
};

export const remove = (uuid: string): Promise<AxiosResponse<void>> => {
  return snippetsClient.delete<void>(`/${uuid}`);
};