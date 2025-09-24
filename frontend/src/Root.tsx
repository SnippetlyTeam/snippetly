import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import LandingPage from "./modules/LandingPage/LandingPage";
import SignInPage from "./modules/AuthPage/SignInPage";
import SignUpPage from "./modules/AuthPage/SignUpPage";
import NotFoundPage from "./modules/NotFoundPage/NotFoundPage";

export const Root = () => (
  <Router>
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<LandingPage />} />
        <Route path="signin" element={<SignInPage />} />
        <Route path="signup" element={<SignUpPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  </Router>
)