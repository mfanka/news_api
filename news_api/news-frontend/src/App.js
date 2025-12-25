import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage";
import CreateEditPage from "./pages/CreateEditPage";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <BrowserRouter>
      <nav className="navbar navbar-dark bg-dark p-2">
        <Link to="/" className="navbar-brand">Новости</Link>
        <Link to="/create" className="btn btn-success">Добавить</Link>
      </nav>

      <div className="container mt-3">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/create" element={<CreateEditPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
