import React from "react";
import { ShieldCheck, Mail, Github, Linkedin } from "lucide-react";

const Footer = () => {
  const pixelTexture = (base, dot) => ({
    backgroundColor: base,
    backgroundImage: `radial-gradient(${dot} 0.7px, transparent 0.7px)`,
    backgroundSize: "10px 10px",
    border: "1px solid rgba(207,214,230,0.9)",
  });

  return (
    <footer className="text-slate-700 official-footer-shell">
      <div className="max-w-7xl mx-auto px-6 py-12 grid md:grid-cols-4 gap-8">
        <div className="rounded-2xl p-5" style={pixelTexture("#f9ffff", "rgba(92,79,190,0.1)")}>
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck className="text-violet-600" size={22} />
            <h2 className="text-xl font-semibold text-slate-800">CampusShield</h2>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">
            AI-powered recruitment fraud detection system helping students
            verify job & internship offers safely before applying or paying.
          </p>
        </div>

        <div className="rounded-2xl p-5" style={pixelTexture("#f8f7ff", "rgba(92,79,190,0.12)")}>
          <h3 className="text-slate-800 font-semibold mb-4">Core Modules</h3>
          <ul className="space-y-2 text-sm text-slate-600">
            <li>Text & OCR Analysis</li>
            <li>ML Fraud Detection</li>
            <li>Behavioral Rule Engine</li>
            <li>Link Safety Scanner</li>
          </ul>
        </div>

        <div className="rounded-2xl p-5" style={pixelTexture("#fffaf5", "rgba(92,79,190,0.09)")}>
          <h3 className="text-slate-800 font-semibold mb-4">Quick Links</h3>
          <ul className="space-y-2 text-sm text-slate-600">
            <li className="hover:text-violet-700 cursor-pointer transition">How It Works</li>
            <li className="hover:text-violet-700 cursor-pointer transition">Risk Categories</li>
            <li className="hover:text-violet-700 cursor-pointer transition">Safety Tips</li>
            <li className="hover:text-violet-700 cursor-pointer transition">Privacy Policy</li>
          </ul>
        </div>

        <div className="rounded-2xl p-5" style={pixelTexture("#f7fbff", "rgba(92,79,190,0.1)")}>
          <h3 className="text-slate-800 font-semibold mb-4">Contact</h3>
          <div className="space-y-3 text-sm text-slate-600">
            <div className="flex items-center gap-2">
              <Mail size={16} />
              <span>support@campusshield.ai</span>
            </div>
            <div className="flex gap-4 pt-2">
              <Github size={18} className="hover:text-violet-700 cursor-pointer transition" />
              <Linkedin size={18} className="hover:text-violet-700 cursor-pointer transition" />
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-300 text-center py-4 text-sm text-slate-500">
        {`© ${new Date().getFullYear()} CampusShield. created by LordCoders.`}
        <br />
        <span className="text-slate-600">
          AI Recruitment Fraud Risk Analysis & Phishing Link Detection System
        </span>
      </div>
    </footer>
  );
};

export default Footer;
