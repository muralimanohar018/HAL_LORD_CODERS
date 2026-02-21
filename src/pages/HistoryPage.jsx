import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";

const historyData = [
  {
    id: "CS-1034",
    company: "TalentBridge Solutions",
    role: "Remote Data Analyst Intern",
    score: 84,
    finalRiskLevel: "HIGH",
    modelVersion: "v2.1",
    date: "Feb 21, 2026 14:32",
    type: "Screenshot OCR",
    summary: "Multiple scam patterns including fee request and suspicious domain mismatch.",
  },
  {
    id: "CS-1033",
    company: "Finverse Careers",
    role: "Investment Analyst Trainee",
    score: 62,
    finalRiskLevel: "HIGH",
    modelVersion: "v2.0",
    date: "Feb 21, 2026 11:09",
    type: "PDF Offer Letter",
    summary: "Suspicious urgency and inconsistent recruiter identity.",
  },
  {
    id: "CS-1032",
    company: "Innotech Systems",
    role: "Software Intern",
    score: 24,
    finalRiskLevel: "LOW",
    modelVersion: "v1.9",
    date: "Feb 20, 2026 18:45",
    type: "Text Message",
    summary: "Mostly legitimate signals with no payment language detected.",
  },
];

const getRisk = (score) => {
  if (score >= 61) return { label: "High Risk", cls: "danger" };
  if (score >= 31) return { label: "Suspicious", cls: "warning" };
  return { label: "Safe", cls: "success" };
};

export default function HistoryPage() {
  const savedHistory = (() => {
    try {
      const parsed = JSON.parse(localStorage.getItem("campusshield-history") || "[]");
      return Array.isArray(parsed) && parsed.length ? parsed : historyData;
    } catch {
      return historyData;
    }
  })();

  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");

  const filtered = useMemo(() => {
    return savedHistory.filter((item) => {
      const matchQuery =
        !query ||
        item.company.toLowerCase().includes(query.toLowerCase()) ||
        item.role.toLowerCase().includes(query.toLowerCase());
      const matchFilter =
        filter === "all" ||
        (filter === "high" && item.score >= 61) ||
        (filter === "suspicious" && item.score >= 31 && item.score < 61) ||
        (filter === "safe" && item.score < 31);
      return matchQuery && matchFilter;
    });
  }, [query, filter, savedHistory]);

  return (
    <div className="min-vh-100 app-page-bg">
      <Navbar />
      <main className="container-lg" style={{ paddingTop: "110px", paddingBottom: "32px" }}>
        <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-3 rounded-4 p-4 official-header-panel">
          <h1 className="display-6 fw-bold text-light mb-1">Scan History</h1>
          <p className="text-secondary mb-0">Review previously analyzed job and internship offers.</p>
        </motion.section>

        <section className="row g-2 mb-3">
          <div className="col-md-6">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search company or role"
              className="form-control bg-dark text-light border-secondary"
            />
          </div>
          <div className="col-md-2">
            <button onClick={() => setFilter("all")} className={`btn w-100 ${filter === "all" ? "btn-info" : "btn-outline-info"}`}>All</button>
          </div>
          <div className="col-md-2">
            <button onClick={() => setFilter("high")} className={`btn w-100 ${filter === "high" ? "btn-danger" : "btn-outline-danger"}`}>High</button>
          </div>
          <div className="col-md-2">
            <button onClick={() => setFilter("safe")} className={`btn w-100 ${filter === "safe" ? "btn-success" : "btn-outline-success"}`}>Safe</button>
          </div>
        </section>

        <section className="d-grid gap-3">
          {filtered.map((item, index) => {
            const risk = getRisk(item.score);
            return (
              <motion.div key={item.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}>
                <div className="card bg-dark bg-opacity-50 border-secondary text-light shadow-sm">
                  <div className="card-body">
                    <div className="d-flex flex-wrap align-items-center gap-2 mb-2">
                      <span className="badge text-bg-info">{item.id}</span>
                      <span className={`badge text-bg-${risk.cls}`}>{risk.label}</span>
                      <span className="small text-secondary">{item.type}</span>
                    </div>
                    <h2 className="h5 fw-bold mb-1">{item.company}</h2>
                    <p className="text-secondary mb-2">{item.role}</p>
                    <p className="text-light-emphasis mb-2">{item.summary}</p>
                    <div className="d-flex flex-wrap gap-2 mb-2">
                      <span className="badge text-bg-dark border border-secondary-subtle">
                        Model: {item.modelVersion || "n/a"}
                      </span>
                      <span className="badge text-bg-secondary">
                        Level: {String(item.finalRiskLevel || (item.score >= 61 ? "HIGH" : item.score >= 31 ? "MEDIUM" : "LOW")).toUpperCase()}
                      </span>
                    </div>
                    <div className="d-flex justify-content-between small text-secondary">
                      <span>{item.date}</span>
                      <span>Risk Score: {item.score}%</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}

          {filtered.length === 0 && (
            <div className="alert alert-secondary text-center mb-0">No matching scans found.</div>
          )}
        </section>
      </main>
      <Footer />
    </div>
  );
}
