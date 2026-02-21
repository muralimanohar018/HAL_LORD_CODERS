import { useState } from "react";
import { motion } from "framer-motion";
import { Link, useLocation, useNavigate } from "react-router-dom";

const navLinks = [
  { path: "/", label: "Home" },
  { path: "/scan", label: "Analysis" },
  { path: "/history", label: "History" },
];

export default function Navbar({ user = { name: "Student", role: "Campus Member" } }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <motion.nav
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.35 }}
      className="position-fixed top-0 start-0 end-0 z-3"
      style={{ paddingTop: "10px" }}
    >
      <div className="container-xl">
        <div className="navbar navbar-expand-md rounded-4 official-navbar-shell px-2 px-md-3 py-2 flex-nowrap overflow-hidden">
          <Link
            to="/"
            className="navbar-brand d-flex align-items-center gap-2 text-light fw-bold m-0 min-w-0"
            style={{ maxWidth: "70%" }}
          >
            <span className="badge text-bg-info">CampusShield</span>
            {/* <span className="text-truncate d-none d-sm-inline">CampusShield</span> */}
          </Link>

          <button
            className="navbar-toggler border-secondary"
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
          >
            <span className="navbar-toggler-icon" />
          </button>

          <div className={`collapse navbar-collapse ${menuOpen ? "show" : ""} w-100`}>
            <ul className="navbar-nav me-auto mb-2 mb-md-0 flex-wrap">
              {navLinks.map((link) => (
                <li key={link.path} className="nav-item">
                  <Link
                    to={link.path}
                    onClick={() => setMenuOpen(false)}
                    className={`nav-link ${location.pathname === link.path ? "active text-info" : "text-light"}`}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>

            <div className="d-flex align-items-center gap-2 flex-wrap">
              <span className="small text-secondary d-none d-md-inline">{user.name}</span>
              <button
                onClick={() => {
                  localStorage.removeItem("campusshield-auth");
                  navigate("/login");
                }}
                className="btn btn-sm btn-outline-danger"
                type="button"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.nav>
  );
}
