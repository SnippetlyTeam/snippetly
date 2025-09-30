import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import LandingPage from "./modules/LandingPage/LandingPage";
import SignInPage from "./modules/AuthPage/SignInPage";
import SignUpPage from "./modules/AuthPage/SignUpPage";
import NotFoundPage from "./modules/NotFoundPage/NotFoundPage";
import PasswordResetPage from "./modules/AuthPage/PasswordResetPage";
import SetNewPasswordPage from "./modules/AuthPage/SetNewPasswordPage";
import FinishRegistrationPage from "./modules/AuthPage/FinishRegistrationPage";
import { AppProvider } from "./contexts/AppContext";

export const Root = () => (
  <Router>
    <AppProvider>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<LandingPage />} />
          <Route path="sign-in" element={<SignInPage />} />
          <Route path="sign-up" element={<SignUpPage />} />
          <Route path="password-reset" element={<PasswordResetPage />} />
          <Route path="set-new-password" element={<SetNewPasswordPage />} />
          <Route path="activate-account">
            <Route index element={<FinishRegistrationPage />} />
            <Route path=":token" element={<FinishRegistrationPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </AppProvider>
  </Router>
)