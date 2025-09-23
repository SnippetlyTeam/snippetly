import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import LandingPage from "./modules/LandingPage/LandingPage";
import LogInPage from "./modules/AuthPage/LogInPage";
import SignUpPage from "./modules/AuthPage/SignUpPage";

export const Root = () => (
  <Router>
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<LandingPage />} />
        <Route path="login" element={<LogInPage/>} />
        <Route path="signup" element={<SignUpPage />} />
      </Route>
    </Routes>
  </Router>
)