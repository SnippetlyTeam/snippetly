export const getFavoriteSnippetsIds = (): string[] => {
  const storedValue = localStorage.getItem('favoriteSnippetsIds');

  if (!storedValue) {
    return [];
  }

  try {
    const parsedValue = JSON.parse(storedValue);

    return Array.isArray(parsedValue) ? parsedValue : [];
  } catch {
    return [];
  }
};

export const saveFavoriteSnippetsIds = (ids: string[]) => {
  if (Array.isArray(ids)) {
    localStorage.setItem('favoriteSnippetsIds', JSON.stringify(ids));
  }
};