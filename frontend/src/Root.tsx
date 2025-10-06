import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import App from "./App";
import LandingPage from "./modules/LandingPage/LandingPage";
import SignInPage from "./modules/AuthPage/SignInPage";
import SignUpPage from "./modules/AuthPage/SignUpPage";
import NotFoundPage from "./modules/NotFoundPage/NotFoundPage";
import PasswordResetPage from "./modules/AuthPage/PasswordResetPage";
import SetNewPasswordPage from "./modules/AuthPage/SetNewPasswordPage";
import FinishRegistrationPage from "./modules/AuthPage/FinishRegistrationPage";
import { AuthProvider } from "./contexts/AuthContext";
import FinishRegistrationTokenPage from "./modules/AuthPage/FinishRegistrationTokenPage";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AuthCallbackPage from "./modules/AuthPage/AuthCallbackPage";
import SnippetsPage from "./modules/SnippetsPage/SnippetsPage";
import SnippetDetailsPage from "./modules/SnippetDetailsPage/SnippetDetailsPage";
import PublicOnlyRoute from "./components/PublicOnlyRoute/PublicOnlyRoute";
import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
    },
  },
});

export const Root = () => (
  <QueryClientProvider client={queryClient}>
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<LandingPage />} />
            <Route
              path="auth/google"
              element={
                <Navigate
                  to={`/auth-callback${window.location.search}`}
                  replace
                />
              }
            />
            <Route path="auth-callback" element={<AuthCallbackPage />} />

            <Route element={<PublicOnlyRoute />}>
              <Route path="sign-in" element={<SignInPage />} />
              <Route path="sign-up" element={<SignUpPage />} />
              <Route path="reset-password">
                <Route index element={<PasswordResetPage />} />
                <Route path=":token" element={<SetNewPasswordPage />} />
              </Route>
              <Route path="activate-account">
                <Route index element={<FinishRegistrationPage />} />
                <Route path=":token" element={<FinishRegistrationTokenPage />} />
              </Route>
            </Route>

            <Route element={<ProtectedRoute />}>
              <Route path="snippets" element={<SnippetsPage />} />
              <Route path="snippets/:snippetId" element={<SnippetDetailsPage />} />
            </Route>

            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  </QueryClientProvider>
)