import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import LandingPage from "./modules/LandingPage/LandingPage";

export const Root = () => (
  <Router>
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<LandingPage />} />
      </Route>
    </Routes>
  </Router>
)