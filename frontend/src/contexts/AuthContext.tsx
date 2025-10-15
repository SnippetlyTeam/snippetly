import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { Loader } from "../components/Loader";

type AccessToken = string | undefined;
type RefreshToken = string | undefined;

type AuthContextType = {
  accessToken: AccessToken;
  isAuthenticated: boolean;
  isTokenLoading: boolean;
  setAccessToken: (token: AccessToken) => void;
  refreshAuthToken: () => Promise<AccessToken>;
  email: string;
  setEmail: (email: string) => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

type Props = {
  children: ReactNode;
}

export const AuthProvider: React.FC<Props> = ({ children }) => {
  const [accessToken, setAccessTokenState] = useState<AccessToken>(undefined);
  const [isTokenLoading, setIsTokenLoading] = useState<boolean>(true);

  const setAccessToken = (token: AccessToken) => setAccessTokenState(token);

  const SERVER_BASE_URL = import.meta.env.VITE_SERVER_BASE_URL;

  const [email, setEmailState] = useState<string>(() => localStorage.getItem('reset_email') || '');

  const setEmail = (newEmail: string) => {
    setEmailState(newEmail);
    if (newEmail) {
      localStorage.setItem('reset_email', newEmail);
    } else {
      localStorage.removeItem('reset_email');
    }
  };

  const refreshAuthToken = async (): Promise<AccessToken> => {
    const storedRefreshToken: RefreshToken = localStorage.getItem('refresh_token') || undefined;

    if (!storedRefreshToken) {
      setAccessToken(undefined);
      return undefined;
    }

    try {
      const response = await fetch(`${SERVER_BASE_URL}/api/v1/auth/refresh`, {
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
      const newAccessToken: AccessToken = data.access_token;
      setAccessToken(newAccessToken);

      return newAccessToken;
    } catch (error) {
      setAccessToken(undefined);
      return undefined;
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
    email,
    setEmail,
    setAccessToken,
    refreshAuthToken,
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