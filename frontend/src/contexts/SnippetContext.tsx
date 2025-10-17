import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getFavoriteSnippetsIds, saveFavoriteSnippetsIds } from "../modules/shared/services/localStorage";

type SnippetContextType = {
  favoriteSnippetsIds: string[],
  setFavoriteSnippetsIds: React.Dispatch<React.SetStateAction<string[]>>,
};

const SnippetContext = createContext<SnippetContextType | null>(null);

type Props = {
  children: ReactNode;
}

export const SnippetProvider: React.FC<Props> = ({ children }) => {
  const [favoriteSnippetsIds, setFavoriteSnippetsIds] = useState<string[]>(getFavoriteSnippetsIds());

  const value: SnippetContextType = {
    favoriteSnippetsIds,
    setFavoriteSnippetsIds,
  };

  useEffect(() => {
    saveFavoriteSnippetsIds(favoriteSnippetsIds);
  }, [favoriteSnippetsIds]);

  return (
    <SnippetContext.Provider value={value}>
      {children}
    </SnippetContext.Provider>
  )
}

export const useSnippetContext = () => {
  const context = useContext(SnippetContext);
  if (!context) {
    throw new Error('useSnippetContext must be used within an SnippetProvider');
  }
  return context;
};