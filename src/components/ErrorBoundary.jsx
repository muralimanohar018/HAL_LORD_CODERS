import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    // Keep a trace in console for debugging deployed crashes.
    console.error("CampusShield frontend runtime error:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-vh-100 d-flex align-items-center justify-content-center app-page-bg px-3">
          <div className="card p-4 text-center shadow-lg" style={{ maxWidth: "640px", width: "100%" }}>
            <h1 className="h4 fw-bold mb-2 text-danger">Something went wrong</h1>
            <p className="text-secondary mb-3">
              The page encountered an unexpected error. Please refresh and try again.
            </p>
            <button
              type="button"
              className="btn btn-info"
              onClick={() => window.location.reload()}
            >
              Reload
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
