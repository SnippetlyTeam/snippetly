import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import LandingPage from "./modules/LandingPage/LandingPage";
import NotFoundPage from "./modules/NotFoundPage/NotFoundPage";

export const Root = () => (
  <Router>
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<LandingPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  </Router>
)