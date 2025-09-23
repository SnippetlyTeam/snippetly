import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import LandingPage from "./modules/LandingPage/LandingPage";
import AuthPage from "./modules/AuthPage/AuthPage";

export const Root = () => (
  <Router>
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<LandingPage />} />
        <Route path="signin" element={<AuthPage formType='signin' />} />
        <Route path="signup" element={<AuthPage formType='signup' />} />
      </Route>
    </Routes>
  </Router>
)