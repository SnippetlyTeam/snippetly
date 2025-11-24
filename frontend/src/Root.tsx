import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
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
import { Toaster } from "react-hot-toast";
import SnippetFormPage from "./modules/SnippetFormPage/SnippetFormPage";
import ProfilePage from "./modules/ProfilePage/ProfilePage";
import Overview from "./modules/ProfilePage/Overview";
import Snippets from "./modules/ProfilePage/Snippets";
import Settings from "./modules/ProfilePage/Settings";
import ProfileRedirector from "./modules/ProfilePage/ProfileRedirector";
import FavoritesPage from "./modules/FavoritesPage/FavoritesPage";
import { SnippetProvider } from "./contexts/SnippetContext";
import Edit from "./modules/ProfilePage/Edit";
import ChangePasswordPage from "./modules/ChangePasswordPage/ChangePasswordPage";

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
    <AuthProvider>
      <Router>
        <SnippetProvider>
          <Routes>
            <Route path="/" element={<App />}>
              <Route index element={<LandingPage />} />
              <Route path="auth/google" element={<AuthCallbackPage />} />

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
                <Route path="snippets">
                  <Route index element={<SnippetsPage />} />
                  <Route path="create" element={<SnippetFormPage />} />
                  <Route path="edit/:snippetId" element={<SnippetFormPage />} />
                  <Route path=":snippetId" element={<SnippetDetailsPage />} />
                </Route>

                <Route path="profile" element={<ProfileRedirector />} />
                <Route path="profile/:username" element={<ProfilePage />}>
                  <Route index element={<Overview />} />
                  <Route path="snippets" element={<Snippets />} />
                  <Route path="settings" element={<Settings />} />
                  <Route path="edit" element={<Edit />} />
                  <Route path="*" element={<NotFoundPage />} />
                </Route>

                <Route path="change-password" element={<ChangePasswordPage />} />
                <Route path="favorites" element={<FavoritesPage />} />
              </Route>

              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </SnippetProvider>
        <Toaster />
      </Router>
    </AuthProvider>
  </QueryClientProvider >
)