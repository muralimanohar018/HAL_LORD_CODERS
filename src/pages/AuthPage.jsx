import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";
import {
  cacheAuthenticatedUser,
  clearCachedAuth,
  isSupabaseConfigured,
  supabase,
} from "../lib/supabaseClient";

const panelStyle = {
  background: "linear-gradient(160deg, rgba(255,255,255,0.98), rgba(248,249,253,0.96))",
  border: "1px solid rgba(207,214,230,0.95)",
  boxShadow: "0 14px 30px rgba(69, 83, 109, 0.12)",
};

const inputStyle = {
  background: "#ffffff",
  color: "#21293c",
  border: "1px solid rgba(166,177,200,0.85)",
};

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    setMode(location.pathname === "/register" ? "register" : "login");
  }, [location.pathname]);

  useEffect(() => {
    let cancelled = false;
    if (!supabase) return () => {};

    supabase.auth.getSession().then(({ data }) => {
      if (!cancelled && data.session) {
        navigate("/dashboard", { replace: true });
      }
    });

    return () => {
      cancelled = true;
    };
  }, [navigate]);

  useEffect(() => {
    if (!supabase) return () => {};

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      const user = session?.user || null;
      if (user) {
        cacheAuthenticatedUser(user);
      } else {
        clearCachedAuth();
      }
    });

    return () => {
      listener.subscription.unsubscribe();
    };
  }, []);

  const update = (key) => (e) => setForm((prev) => ({ ...prev, [key]: e.target.value }));
  const emailRedirectTo = `${window.location.origin}/login`;

  const getReadableAuthError = (rawMessage, authMode) => {
    const message = String(rawMessage || "").toLowerCase();
    if (!message) return authMode === "login" ? "Login failed." : "Signup failed.";

    if (message.includes("invalid login credentials")) {
      return "Invalid email/password. If you just registered, verify your email first.";
    }
    if (message.includes("email not confirmed")) {
      return "Email not verified. Open the verification link from your inbox, then sign in.";
    }
    if (message.includes("user already registered")) {
      return "Account already exists. Please sign in.";
    }
    if (message.includes("password should be at least")) {
      return "Password must be at least 6 characters.";
    }
    return rawMessage;
  };

  const resendVerificationEmail = async () => {
    if (!supabase || !pendingVerificationEmail) return;
    setResending(true);
    setError("");
    try {
      const { error: resendError } = await supabase.auth.resend({
        type: "signup",
        email: pendingVerificationEmail,
        options: { emailRedirectTo },
      });
      if (resendError) {
        setError(getReadableAuthError(resendError.message, "register") || "Could not resend verification email.");
        return;
      }
      setInfo(`Verification email sent to ${pendingVerificationEmail}.`);
    } finally {
      setResending(false);
    }
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim());

    if (mode === "register") {
      if (!form.name.trim() || !form.email.trim() || !form.password || !form.confirm) {
        setError("Please fill all required fields.");
        return;
      }
      if (!emailValid) {
        setError("Please enter a valid email address.");
        return;
      }
      if (form.password.length < 6) {
        setError("Password must be at least 6 characters.");
        return;
      }
      if (form.password !== form.confirm) {
        setError("Password and confirm password do not match.");
        return;
      }
    } else {
      if (!form.email.trim() || !form.password) {
        setError("Email and password are required.");
        return;
      }
      if (!emailValid) {
        setError("Please enter a valid email address.");
        return;
      }
    }

    if (!isSupabaseConfigured || !supabase) {
      setError("Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.");
      return;
    }

    setError("");
    setInfo("");
    setLoading(true);

    try {
      if (mode === "login") {
        const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
          email: form.email.trim(),
          password: form.password,
        });

        if (signInError) {
          setError(getReadableAuthError(signInError.message, "login") || "Login failed.");
          return;
        }

        if (signInData?.user) {
          cacheAuthenticatedUser(signInData.user);
        }
        setPendingVerificationEmail("");
        navigate("/dashboard", { replace: true });
        return;
      }

      const { error: signUpError, data } = await supabase.auth.signUp({
        email: form.email.trim(),
        password: form.password,
        options: {
          data: { name: form.name.trim() },
          emailRedirectTo,
        },
      });

      if (signUpError) {
        setError(getReadableAuthError(signUpError.message, "register") || "Signup failed.");
        return;
      }

      if (data?.user) {
        cacheAuthenticatedUser(data.user);
      }

      if (data.session) {
        setPendingVerificationEmail("");
        navigate("/dashboard", { replace: true });
        return;
      }

      setPendingVerificationEmail(form.email.trim());
      setInfo("Registration successful. Please verify your email, then sign in.");
      setForm((prev) => ({ ...prev, password: "", confirm: "" }));
      setMode("login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-vh-100 app-page-bg"
    >
      <Navbar />
      <div className="container-xl" style={{ paddingTop: "88px", paddingBottom: "34px" }}>
        <Link
          to="/"
          className="btn btn-outline-light rounded-3 px-3 py-2 mb-4"
          style={{ borderColor: "#5c4fbe", color: "#5c4fbe" }}
        >
          Back to Home
        </Link>

        <div className="row g-4">
          <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="col-lg-6">
            <div className="card h-100 rounded-3" style={panelStyle}>
              <div className="card-body p-4 p-md-5 text-light">
                <p className="text-uppercase mb-3" style={{ color: "#5c4fbe", letterSpacing: "0.08em" }}>
                  Welcome to CampusShield
                </p>
                <h1 className="display-5 fw-bold mb-3" style={{ color: "#21293c" }}>
                  Protect your career search
                </h1>

                {mode === "login" && (
                  <>
                    <p className="fs-4 mb-4" style={{ color: "#5b6883", lineHeight: 1.45 }}>
                      Sign in to analyze suspicious job offers, store your reports, and track scam patterns over time.
                    </p>
                  </>
                )}

                {mode === "register" && (
                  <>
                    <p className="fs-4 mb-4" style={{ color: "#5b6883", lineHeight: 1.45 }}>
                      Create your account to start scanning suspicious offers, screenshots, and PDFs with one secure dashboard.
                    </p>
                    <div className="alert py-3 rounded-3 border-0 mb-3" style={{ background: "#eefffd", color: "#2a3039" }}>
                      Scan history in one place
                    </div>
                    <div className="alert py-3 rounded-3 border-0 mb-3" style={{ background: "#fff6ee", color: "#2a3039" }}>
                      Actionable risk insights
                    </div>
                    <div className="fs-4" style={{ color: "#5b6883" }}>Flow: Register - Upload - Analyze</div>
                  </>
                )}
              </div>
            </div>
          </motion.section>

          <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }} className="col-lg-6">
            <div className="card rounded-3" style={panelStyle}>
              <div className="card-body p-4 p-md-5 text-light">
                <div className="btn-group w-100 mb-4" role="group" aria-label="Auth tabs">
                  <button
                    type="button"
                    onClick={() => setMode("login")}
                    className="btn py-2 rounded-start-3"
                    style={{
                      background: mode === "login" ? "linear-gradient(135deg, #5c4fbe, #7366d8)" : "#ffffff",
                      color: mode === "login" ? "#ffffff" : "#5c4fbe",
                      border: "1px solid #5c4fbe",
                      fontWeight: 600,
                    }}
                  >
                    Login
                  </button>
                  <button
                    type="button"
                    onClick={() => setMode("register")}
                    className="btn py-2 rounded-end-3"
                    style={{
                      background: mode === "register" ? "linear-gradient(135deg, #5c4fbe, #7366d8)" : "#ffffff",
                      color: mode === "register" ? "#ffffff" : "#5c4fbe",
                      border: "1px solid #5c4fbe",
                      fontWeight: 600,
                    }}
                  >
                    Register
                  </button>
                </div>

                <form onSubmit={onSubmit} className="d-grid gap-3">
                  {mode === "register" && (
                    <>
                      <div>
                        <label className="form-label text-light mb-1">Name</label>
                        <input
                          type="text"
                          value={form.name}
                          onChange={update("name")}
                          placeholder="Enter full name"
                          required
                          className="form-control rounded-3 py-3"
                          style={inputStyle}
                        />
                      </div>
                      <div>
                        <label className="form-label text-light mb-1">Email</label>
                        <input
                          type="email"
                          value={form.email}
                          onChange={update("email")}
                          placeholder="Enter email"
                          required
                          className="form-control rounded-3 py-3"
                          style={inputStyle}
                        />
                      </div>
                      <div>
                        <label className="form-label text-light mb-1">Create Password</label>
                        <input
                          type="password"
                          value={form.password}
                          onChange={update("password")}
                          placeholder="Create password"
                          required
                          className="form-control rounded-3 py-3"
                          style={inputStyle}
                        />
                      </div>
                      <div>
                        <label className="form-label text-light mb-1">Confirm Password</label>
                        <input
                          type="password"
                          value={form.confirm}
                          onChange={update("confirm")}
                          placeholder="Re-enter password"
                          required
                          className="form-control rounded-3 py-3"
                          style={inputStyle}
                        />
                      </div>
                    </>
                  )}

                  {mode === "login" && (
                    <>
                      <div>
                        <label className="form-label text-light mb-1">Email</label>
                        <input
                          type="email"
                          value={form.email}
                          onChange={update("email")}
                          placeholder="Enter email"
                          required
                          className="form-control rounded-3 py-3"
                          style={inputStyle}
                        />
                      </div>
                      <div>
                        <label className="form-label text-light mb-1">Password</label>
                        <input
                          type="password"
                          value={form.password}
                          onChange={update("password")}
                          placeholder="Enter password"
                          required
                          className="form-control rounded-3 py-3"
                          style={inputStyle}
                        />
                      </div>
                    </>
                  )}

                  {error && (
                    <div className="alert alert-danger py-2 mb-0 rounded-3 small">
                      {error}
                    </div>
                  )}
                  {info && (
                    <div className="alert alert-info py-2 mb-0 rounded-3 small">
                      {info}
                    </div>
                  )}
                  {pendingVerificationEmail && (
                    <button
                      type="button"
                      className="btn btn-outline-info rounded-3 py-2"
                      onClick={resendVerificationEmail}
                      disabled={resending}
                    >
                      {resending ? "Sending..." : "Resend verification email"}
                    </button>
                  )}

                  <button
                    type="submit"
                    className="btn rounded-3 py-3"
                    style={{ background: "linear-gradient(135deg, #5c4fbe, #7366d8)", color: "#ffffff", fontWeight: 700 }}
                    disabled={loading}
                  >
                    {loading ? "Processing..." : mode === "login" ? "Sign In" : "Create Account"}
                  </button>
                </form>
              </div>
            </div>
          </motion.section>
        </div>
      </div>
      <Footer />
    </div>
  );
}
