export type FiltersType = {
  page?: number;
  per_page?: number;
  tags?: string[];
  language?: string;
  created_before?: string;
  created_after?: string;
  username?: string;
  visibility?: boolean;
}