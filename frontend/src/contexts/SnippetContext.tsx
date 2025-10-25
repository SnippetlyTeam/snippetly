import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getFavorites } from "../api/snippetsClient";
import { useAuthContext } from "./AuthContext";

type SnippetContextType = {
  favoriteSnippetsIds: string[],
  setFavoriteSnippetsIds: React.Dispatch<React.SetStateAction<string[]>>,
};

const SnippetContext = createContext<SnippetContextType | null>(null);

type Props = {
  children: ReactNode;
}

export const SnippetProvider: React.FC<Props> = ({ children }) => {
  const [favoriteSnippetsIds, setFavoriteSnippetsIds] = useState<string[]>([]);
  const { accessToken } = useAuthContext();

  const value: SnippetContextType = {
    favoriteSnippetsIds,
    setFavoriteSnippetsIds,
  };

  useEffect(() => {
    (async () => {
      try {
        const response = await getFavorites(accessToken);
        if (response && response.data && Array.isArray(response.data.snippets)) {
          setFavoriteSnippetsIds(response.data.snippets.map(snip => snip.uuid));
        } else {
          setFavoriteSnippetsIds([]);
        }
      } catch (err) {
        setFavoriteSnippetsIds([]);
      }
    })();
  }, [accessToken]);

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