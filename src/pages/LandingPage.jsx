import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";

const inputs = [
  {
    title: "Text Message Scan",
    desc: "Paste suspicious job or internship text from email, WhatsApp, Telegram, or LinkedIn.",
  },
  {
    title: "Screenshot OCR",
    desc: "Upload JPG or PNG chats. CampusShield extracts recruiter text using OCR.",
  },
  {
    title: "Offer Letter PDF",
    desc: "Upload appointment letters for structure and wording analysis.",
  },
];

export default function LandingPage() {
  return (
    <div
      className="min-vh-100 app-page-bg"
    >
      <Navbar />

      <main className="container-xl" style={{ paddingTop: "110px", paddingBottom: "40px" }}>
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card official-header-panel text-light text-center mb-4"
        >
          <div className="card-body p-4 p-md-5">
            <p className="text-info text-uppercase small mb-2" style={{ letterSpacing: "0.1em" }}>CampusShield</p>
            <h1 className="display-5 fw-bold mb-3">AI-based fake job and internship scam detection for students</h1>
            <p className="text-secondary mx-auto" style={{ maxWidth: "820px" }}>
              CampusShield analyzes recruitment offers and reports whether they appear safe, suspicious, or high risk based on language, behavior, and link authenticity. It does not legally certify company legitimacy.
            </p>
            <Link to="/scan" className="btn btn-info px-4 mt-2">Start Analysis</Link>
          </div>
        </motion.section>

        <section className="row g-3">
          {inputs.map((item, idx) => (
            <motion.article
              key={item.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.08 }}
              className="col-md-4"
            >
              <div className="card h-100 bg-dark bg-opacity-50 border-info-subtle text-light shadow-sm">
                <div className="card-body">
                  <h2 className="h4 fw-bold mb-2">{item.title}</h2>
                  <p className="text-secondary mb-0">{item.desc}</p>
                </div>
              </div>
            </motion.article>
          ))}
        </section>
      </main>
      <Footer />
    </div>
  );
}
