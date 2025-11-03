import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { Loader } from "../components/Loader";
import type { AccessToken } from "../types/Tokens";
import { refresh } from "../api/authClient";

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
    const response = await refresh();
    const newAccessToken: AccessToken = response.data.access_token;
    setAccessToken(newAccessToken);

    return newAccessToken;
  };

  useEffect(() => {
    const attemptRestoreSession = async () => {
      try {
        await refreshAuthToken();
      } catch (error) {
        setAccessToken(undefined);
      } finally {
        setIsTokenLoading(false);
      }
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