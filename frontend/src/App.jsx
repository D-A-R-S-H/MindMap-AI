import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Diagnostic from "./pages/Diagnostic";
import SpeakRecall from "./pages/SpeakRecall";
import Results from "./pages/Results";
import Mastery from "./pages/Mastery";
import Revision from "./pages/Revision";
import Teacher from "./pages/Teacher";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/diagnostic" element={<Diagnostic />} />
          <Route path="/recall" element={<SpeakRecall />} />
          <Route path="/results" element={<Results />} />
          <Route path="/mastery" element={<Mastery />} />
          <Route path="/revision" element={<Revision />} />
          <Route path="/teacher" element={<Teacher />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}