import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { Loader } from "../components/Loader";

type AuthContextType = {
  accessToken: string | null;
  isAuthenticated: boolean;
  isTokenLoading: boolean;
  setAccessToken: (token: string | null) => void;
  refreshAuthToken: () => Promise<string | null>;
};

const AuthContext = createContext<AuthContextType | null>(null);

type Props = {
  children: ReactNode;
}

export const AuthProvider: React.FC<Props> = ({ children }) => {
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [isTokenLoading, setIsTokenLoading] = useState<boolean>(true);

  const setAccessToken = (token: string | null) => setAccessTokenState(token);

  const refreshAuthToken = async (): Promise<string | null> => {
    const storedRefreshToken = localStorage.getItem('refresh_token');

    if (!storedRefreshToken) {
      setAccessToken(null);
      return null;
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: storedRefreshToken })
      });

      if (!response.ok) {
        localStorage.removeItem('refresh_token');
        throw new Error('Failed to refresh auth token');
      }

      const data = await response.json();
      const newAccessToken = data.access_token;
      setAccessToken(newAccessToken);

      return newAccessToken;
    } catch (error) {
      console.log(error)
      setAccessToken(null);
      return null;
    }
  };

  useEffect(() => {
    const attemptRestoreSession = async () => {
      await refreshAuthToken();

      setIsTokenLoading(false);
    };

    attemptRestoreSession();
  }, []);

  const value: AuthContextType = {
    accessToken,
    isAuthenticated: !!accessToken,
    isTokenLoading,
    setAccessToken,
    refreshAuthToken
  };

  if (isTokenLoading) {
    return (
      <main
        style={{
          display: 'flex',
          minHeight: '100vh',
        }}
      >
        <Loader />
      </main>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};