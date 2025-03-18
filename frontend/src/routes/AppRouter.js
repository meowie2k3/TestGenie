import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "../pages/Home/Home";
import Diagram from "../pages/Diagram/Diagram";

export default function AppRouter() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/diagram" element={<Diagram />} />
      </Routes>
    </Router>
  );
}
