import type { SnippetType } from "./SnippetType";

export type SnippetListResponse = {
  page: number;
  per_page: number;
  total_items: number;
  total_pages: number;
  prev_page: string;
  next_page: string;
  snippets: SnippetType[];
};