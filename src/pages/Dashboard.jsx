import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";
import { analyzeFile, analyzeText, BackendApiError, checkBackendHealth, getBackendBaseUrl } from "../lib/backendApi";
import { getAccessToken, getCachedUserId, isSupabaseConfigured } from "../lib/supabaseClient";

const reasonsByScore = (score) => {
  if (score >= 61) {
    return [
      "Payment requested before hiring confirmation",
      "No interview but immediate joining pressure",
      "Link domain does not match stated company",
      "Recruiter uses personal email or messaging app only",
    ];
  }
  if (score >= 31) {
    return [
      "Mixed credibility signals in recruiter message",
      "Domain age is recent compared to company claim",
      "Job language includes urgency and limited seats",
    ];
  }
  return [
    "No upfront payment indicators detected",
    "Communication pattern appears consistent",
    "URL structure and language look normal",
  ];
};

const categoryLabel = (score) => {
  if (score >= 61) return "High Risk Scam";
  if (score >= 31) return "Suspicious";
  return "Safe";
};

const levelClass = (score) => {
  if (score >= 61) return "danger";
  if (score >= 31) return "warning";
  return "success";
};

const labelFromRiskLevel = (level, fallbackScore) => {
  const norm = String(level || "").toUpperCase();
  if (norm === "HIGH") return "High Risk Scam";
  if (norm === "MEDIUM") return "Suspicious";
  if (norm === "LOW") return "Safe";
  return categoryLabel(fallbackScore);
};

const mapAnalysisResponse = (apiJson, fallbackProcessedText = "") => {
  const data = apiJson?.data && typeof apiJson.data === "object" ? apiJson.data : (apiJson || {});
  const rawRiskLevel = String(data?.final_risk_level || "").toUpperCase();
  const probabilityPct = Number.isFinite(data?.ml_scam_probability)
    ? Math.round(data.ml_scam_probability * 100)
    : null;
  const score = Number.isFinite(data?.risk_score)
    ? Math.round(data.risk_score)
    : Number.isFinite(data?.security_risk_score)
    ? Math.round(data.security_risk_score)
    : (probabilityPct ?? 0);

  const behaviorWarnings = Array.isArray(data.behavior_warnings) ? data.behavior_warnings : [];
  const emailWarnings = Array.isArray(data.email_warnings) ? data.email_warnings : [];
  const domainWarnings = Array.isArray(data.domain_warnings) ? data.domain_warnings : [];
  const whoisWarnings = Array.isArray(data.whois_warnings) ? data.whois_warnings : [];
  const signalWarnings = Array.isArray(data.signals) ? data.signals : [];
  const reasons = [...behaviorWarnings, ...emailWarnings, ...domainWarnings, ...whoisWarnings, ...signalWarnings];

  const urls = Array.isArray(data.urls_found) ? data.urls_found : [];
  const phishing = Boolean(data?.security?.phishing);
  const companyStatus = String(data?.company_verification_status || "UNKNOWN");
  const derivedRiskLevel = rawRiskLevel || (score >= 61 ? "HIGH" : score >= 31 ? "MEDIUM" : "LOW");

  return {
    score,
    category: labelFromRiskLevel(derivedRiskLevel, score),
    finalRiskLevel: derivedRiskLevel,
    reasons: reasons.length ? reasons : reasonsByScore(score),
    links: urls,
    modelVersion: data?.model_version || "n/a",
    mlIsScam: Boolean(data?.ml_is_scam),
    mlProbability: Number.isFinite(data?.ml_scam_probability) ? data.ml_scam_probability : null,
    processedText: String(data?.processed_text || data?.extracted_text || fallbackProcessedText || ""),
    companyInferred: data?.company_inferred || "Unknown",
    companyVerificationStatus: companyStatus,
    metrics: [
      probabilityPct ?? Math.min(100, score),
      Math.min(100, behaviorWarnings.length * 22 || Math.round(score * 0.6)),
      phishing ? Math.max(70, score) : Math.min(100, urls.length * 18 || Math.round(score * 0.5)),
      companyStatus === "MATCH" ? 82 : companyStatus === "MISMATCH" ? 28 : 50,
    ],
    threshold: data?.decision_thresholds?.scam_threshold ?? data?.decision_thresholds?.legacy?.ml_probability_gte,
    decisionThresholds: data?.decision_thresholds || null,
  };
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [inputType, setInputType] = useState("text");
  const [message, setMessage] = useState("");
  const [pdfFile, setPdfFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [authPrompt, setAuthPrompt] = useState("");
  const [apiError, setApiError] = useState("");
  const [backendStatus, setBackendStatus] = useState({ state: "checking", latencyMs: null });
  const [activeEndpoint, setActiveEndpoint] = useState("");

  const metrics = useMemo(() => {
    if (!result) return [40, 42, 45, 38];
    if (Array.isArray(result.metrics)) return result.metrics;
    const base = result.score;
    return [base, Math.max(0, base - 10), Math.max(0, base - 5), Math.max(0, base - 15)];
  }, [result]);

  useEffect(() => {
    let mounted = true;

    async function pingBackend() {
      setBackendStatus({ state: "checking", latencyMs: null });
      try {
        const { payload, latencyMs } = await checkBackendHealth();
        if (!mounted) return;
        setBackendStatus({
          state: payload?.status === "ok" ? "connected" : "unknown",
          latencyMs,
        });
      } catch {
        if (!mounted) return;
        setBackendStatus({ state: "disconnected", latencyMs: null });
      }
    }

    pingBackend();
    return () => {
      mounted = false;
    };
  }, []);

  const runScan = async () => {
    if (inputType === "text" && !message.trim()) return;
    if ((inputType === "screenshot" || inputType === "pdf") && !pdfFile) return;

    if (!isSupabaseConfigured) {
      setAuthPrompt("Supabase auth is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.");
      return;
    }

    const token = await getAccessToken();
    if (!token) {
      setAuthPrompt("Please log in first. Your Supabase access token is required by backend.");
      navigate("/login");
      return;
    }

    setAuthPrompt("");
    setApiError("");
    setActiveEndpoint(inputType === "text" ? "/analyze" : "/ocr/extract");
    setScanning(true);
    setResult(null);
    try {
      const apiJson = inputType === "text"
        ? await analyzeText(message)
        : await analyzeFile(pdfFile);
      const resolvedResult = mapAnalysisResponse(apiJson, inputType === "text" ? message.trim() : "");
      setResult(resolvedResult);

      const historyItem = {
        id: `CS-${Date.now().toString().slice(-4)}`,
        company: inputType === "text" ? "Message Submission" : "Uploaded File",
        role:
          inputType === "text"
            ? (message.trim().slice(0, 52) || "Recruiter message analysis")
            : (pdfFile?.name || "Document analysis"),
        score: resolvedResult.score,
        date: new Date().toLocaleString(),
        type: inputType === "text" ? "Text Message" : inputType === "screenshot" ? "Screenshot OCR" : "PDF Offer Letter",
        summary: resolvedResult.reasons.join(" | "),
        modelVersion: resolvedResult.modelVersion || "n/a",
        finalRiskLevel: resolvedResult.finalRiskLevel || (resolvedResult.score >= 61 ? "HIGH" : resolvedResult.score >= 31 ? "MEDIUM" : "LOW"),
      };

      const existing = JSON.parse(localStorage.getItem("campusshield-history") || "[]");
      localStorage.setItem("campusshield-history", JSON.stringify([historyItem, ...existing].slice(0, 30)));
    } catch (error) {
      if (error instanceof BackendApiError) {
        if (error.status === 401) {
          setAuthPrompt("Session expired or unauthorized. Please log in again.");
          navigate("/login");
        } else if (error.status === 422) {
          setApiError(error.message || "Invalid input. Please check your text/file and try again.");
        } else if (error.status === 502) {
          setApiError("ML service failed while processing this request. Please retry.");
        } else if (error.status === 503) {
          setApiError("Service is temporarily unavailable. Please retry in a moment.");
        } else {
          setApiError(error.message || "Backend request failed.");
        }
      } else {
        setApiError("Network error while contacting backend.");
      }
    } finally {
      setScanning(false);
    }
  };

  const handleFilePick = (file) => {
    if (!file) return;
    setPdfFile(file);
  };

  return (
    <div
      className="min-vh-100 position-relative app-page-bg"
    >
      <Navbar />

      <main className="container-xl pb-4" style={{ paddingTop: "150px" }}>
        <motion.section initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="mb-4 rounded-4 p-4 official-header-panel">
          <p className="text-info text-uppercase small mb-1" style={{ letterSpacing: "0.12em" }}>CampusShield Analyzer</p>
          <h1 className="text-light fw-bold display-6 mb-2">Recruitment Fraud Risk Analysis</h1>
          <p className="text-light-emphasis mb-0">Upload suspicious recruitment content and receive an explainable risk report.</p>
        </motion.section>

        <section className="row g-4">
          <div className="col-lg-8">
            <div className="card border-info-subtle bg-dark bg-opacity-50 text-light shadow-lg">
              <div className="card-body p-4">
                <h2 className="h4 fw-bold mb-1">New Scan</h2>
                <p className="text-secondary mb-3">Supported inputs: text message, screenshot OCR, and offer letter PDF.</p>

                <div className="btn-group mb-3" role="group" aria-label="Input type">
                  {["text", "screenshot", "pdf"].map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setInputType(type)}
                      className={`btn ${inputType === type ? "btn-info" : "btn-outline-info"} text-capitalize`}
                    >
                      {type}
                    </button>
                  ))}
                </div>

                {inputType === "text" ? (
                  <textarea
                    className="form-control bg-dark text-light border-secondary"
                    style={{ minHeight: "190px" }}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Paste suspicious recruiter message..."
                  />
                ) : (
                  <label
                    className="d-flex flex-column align-items-center justify-content-center text-center border border-2 border-info-subtle rounded-4 p-4 bg-info bg-opacity-10"
                    style={{ minHeight: "220px", cursor: "pointer", borderStyle: "dashed" }}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => {
                      e.preventDefault();
                      const file = e.dataTransfer.files?.[0] || null;
                      handleFilePick(file);
                    }}
                  >
                    <div className="fs-2 mb-2">Upload</div>
                    <p className="mb-1 fw-semibold text-light">
                      {inputType === "screenshot" ? "Drag screenshot here" : "Drag PDF here"}
                    </p>
                    <p className="small text-secondary mb-0">or click to browse files</p>
                    <input
                      type="file"
                      className="d-none"
                      accept={inputType === "screenshot" ? "image/png,image/jpeg,image/jpg" : ".pdf,application/pdf"}
                      onChange={(e) => handleFilePick(e.target.files?.[0] || null)}
                    />
                  </label>
                )}

                <div className="d-flex flex-wrap gap-2 mt-3 align-items-center">
                  <button
                    type="button"
                    onClick={runScan}
                    className="btn btn-info"
                    disabled={scanning}
                  >
                    {scanning ? "Analyzing..." : "Run Risk Analysis"}
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-light"
                    onClick={() => {
                      setMessage("");
                      setResult(null);
                      setPdfFile(null);
                    }}
                  >
                    Clear
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-info"
                    onClick={() => navigate("/history")}
                  >
                    View History
                  </button>
                  {scanning && <span className="small text-info">PIPELINE EXECUTING...</span>}
                </div>

                {authPrompt && (
                  <div className="alert alert-warning d-flex justify-content-between align-items-center mt-3 mb-0 py-2">
                    <span className="small">{authPrompt}</span>
                    <button onClick={() => navigate("/login")} className="btn btn-sm btn-outline-warning">Go to Login</button>
                  </div>
                )}
                {apiError && (
                  <div className="alert alert-danger mt-3 mb-0 py-2 small">
                    {apiError}
                  </div>
                )}

                {pdfFile && (
                  <p className="small text-secondary mt-2 mb-0 text-end">
                    Selected: <span className="text-light">{pdfFile.name}</span>
                  </p>
                )}
                <p className="small text-secondary mt-2 mb-0">
                  Backend: <span className="text-light">{getBackendBaseUrl()}</span>
                </p>
                <p className="small text-secondary mt-1 mb-0">
                  Backend health:{" "}
                  <span className="text-light">
                    {backendStatus.state}
                    {typeof backendStatus.latencyMs === "number" ? ` (${backendStatus.latencyMs} ms)` : ""}
                  </span>
                </p>
                <p className="small text-secondary mt-1 mb-0">
                  User ID: <span className="text-light">{getCachedUserId() || "not available"}</span>
                </p>
                {activeEndpoint && (
                  <p className="small text-secondary mt-1 mb-0">
                    Last endpoint used: <span className="text-light">{activeEndpoint}</span>
                  </p>
                )}
              </div>
            </div>

            <AnimatePresence>
              {result && (
                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="mt-4">
                  <div className={`card border-${levelClass(result.score)} bg-dark bg-opacity-50 text-light shadow-lg`}>
                    <div className="card-body p-4">
                      {result.mlIsScam && (
                        <div className="alert alert-danger py-2 mb-3">
                          ML classifier flagged this as likely scam content.
                        </div>
                      )}
                      <div className="d-flex flex-column flex-md-row gap-4 align-items-start">
                        <div className="text-center">
                          <div className={`display-5 fw-bold text-${levelClass(result.score)}`}>{result.score}%</div>
                          <span className={`badge text-bg-${levelClass(result.score)} mt-1`}>{result.category}</span>
                          {typeof result.mlProbability === "number" && (
                            <p className="small text-secondary mt-2 mb-0">
                              ML scam probability: {Math.round(result.mlProbability * 100)}%
                            </p>
                          )}
                        </div>

                        <div className="flex-grow-1">
                          <h3 className="h4 fw-bold mb-1">{result.category}</h3>
                          <p className="text-secondary mb-3">This is a preventive risk estimate, not a legal verification.</p>

                          <div className="mb-2">
                            <small className="text-secondary">Language Classifier</small>
                            <div className="progress" role="progressbar" aria-valuenow={metrics[0]} aria-valuemin="0" aria-valuemax="100">
                              <div className="progress-bar bg-info" style={{ width: `${metrics[0]}%` }} />
                            </div>
                          </div>
                          <div className="mb-2">
                            <small className="text-secondary">Behavioral Rules</small>
                            <div className="progress"><div className="progress-bar bg-warning" style={{ width: `${metrics[1]}%` }} /></div>
                          </div>
                          <div className="mb-2">
                            <small className="text-secondary">Link Safety</small>
                            <div className="progress"><div className="progress-bar bg-danger" style={{ width: `${metrics[2]}%` }} /></div>
                          </div>
                          <div>
                            <small className="text-secondary">Company Match</small>
                            <div className="progress"><div className="progress-bar bg-success" style={{ width: `${metrics[3]}%` }} /></div>
                          </div>
                        </div>
                      </div>

                      <hr className="border-secondary my-4" />

                      <p className="small text-info text-uppercase mb-2">Processed Text</p>
                      <div className="border border-secondary rounded-3 p-3 small bg-dark bg-opacity-25 mb-3">
                        {result.processedText || "No processed text returned by backend."}
                      </div>

                      <p className="small text-info text-uppercase mb-2">Technical Info</p>
                      <div className="row g-2 mb-3">
                        <div className="col-12 col-md-6">
                          <div className="border border-secondary rounded-3 p-2 small bg-dark bg-opacity-25">
                            Model: <span className="text-light">{result.modelVersion}</span>
                          </div>
                        </div>
                        <div className="col-12 col-md-6">
                          <div className="border border-secondary rounded-3 p-2 small bg-dark bg-opacity-25">
                            Company: <span className="text-light">{result.companyInferred}</span> ({result.companyVerificationStatus})
                          </div>
                        </div>
                        {typeof result.threshold === "number" && (
                          <div className="col-12">
                            <div className="border border-secondary rounded-3 p-2 small bg-dark bg-opacity-25">
                              Decision threshold: <span className="text-light">{result.threshold}</span>
                            </div>
                          </div>
                        )}
                      </div>

                      <p className="small text-info text-uppercase mb-2">Explanation</p>
                      <div className="row g-2">
                        {result.reasons.map((reason) => (
                          <div key={reason} className="col-12 col-md-6">
                            <div className="border border-secondary rounded-3 p-2 small text-light-emphasis bg-dark bg-opacity-25">{reason}</div>
                          </div>
                        ))}
                      </div>

                      <p className="small text-info text-uppercase mt-4 mb-2">Suspicious Links Detected</p>
                      <div className="d-flex flex-wrap gap-2">
                        {result.links.length > 0 ? (
                          result.links.map((link) => (
                            <span key={link} className="badge text-bg-danger-subtle border border-danger-subtle text-danger">
                              {link}
                            </span>
                          ))
                        ) : (
                          <span className="small text-secondary">No URLs found.</span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="col-lg-4">
            <div className="card border-info-subtle bg-dark bg-opacity-50 text-light shadow-lg h-100">
              <div className="card-body p-4">
                <h2 className="h4 fw-bold">Safety Advice</h2>
                <p className="text-secondary">Use this checklist before responding to any recruiter message or internship offer.</p>

                <div className="mt-3">
                  <p className="small text-info text-uppercase mb-2">Before You Apply</p>
                  <ul className="small text-light-emphasis ps-3">
                    <li>Never pay registration, training, or onboarding fees before verification.</li>
                    <li>Check recruiter email domain against the official company website domain.</li>
                    <li>Search company careers page manually instead of trusting forwarded links.</li>
                    <li>Confirm job role, salary, and location consistency across all communication.</li>
                  </ul>
                </div>

                <div className="mt-3">
                  <p className="small text-info text-uppercase mb-2">Red Flags</p>
                  <ul className="small text-light-emphasis ps-3">
                    <li>Urgent pressure like "apply in 10 minutes" or "limited seats only".</li>
                    <li>No interview process but immediate joining confirmation.</li>
                    <li>Requests for Aadhaar, PAN, bank details, or OTP too early.</li>
                    <li>Communication only through WhatsApp/Telegram with personal numbers.</li>
                  </ul>
                </div>

                <div className="alert alert-warning mt-3 mb-0">
                  <p className="small fw-semibold mb-1">If Suspicious</p>
                  <p className="small mb-0">Do not make payment, do not share sensitive documents, and verify directly through official company contacts.</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
