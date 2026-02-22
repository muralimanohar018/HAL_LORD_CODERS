import { getAccessToken } from "./supabaseClient";

const backendBaseUrl = (import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

export class BackendApiError extends Error {
  constructor(message, status, payload = null) {
    super(message);
    this.name = "BackendApiError";
    this.status = status;
    this.payload = payload;
  }
}

function extractErrorMessage(payload, fallback) {
  if (typeof payload === "string") return payload;
  if (payload && typeof payload === "object") {
    const detail = payload.detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object") {
      if (typeof detail.message === "string") return detail.message;
      if (typeof detail.ml_detail === "string") return detail.ml_detail;
    }
    if (typeof payload.message === "string") return payload.message;
  }
  return fallback;
}

async function fetchWithAuth(path, init = {}) {
  const token = await getAccessToken();
  const headers = new Headers(init.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${backendBaseUrl}${path}`, {
    ...init,
    headers,
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const defaultMessage = `Backend request failed (${response.status})`;
    const message = extractErrorMessage(payload, defaultMessage);
    throw new BackendApiError(message, response.status, payload);
  }

  return payload;
}

function isFallbackStatus(error) {
  return error instanceof BackendApiError && [404, 405, 415, 422].includes(error.status);
}

export async function analyzeText(text) {
  const trimmed = String(text || "").trim();
  if (!trimmed) {
    throw new BackendApiError("Text is required", 422);
  }

  try {
    // Contract format.
    return await fetchWithAuth("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: trimmed }),
    });
  } catch (error) {
    if (!isFallbackStatus(error)) throw error;
  }

  try {
    // Alternate backend contract used in some CampusShield branches.
    return await fetchWithAuth("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ original_text: trimmed, extracted_text: trimmed }),
    });
  } catch (error) {
    if (!isFallbackStatus(error)) throw error;
  }

  // Form fallback for legacy route variant.
  const form = new FormData();
  form.append("text", trimmed);
  return fetchWithAuth("/analyze", {
    method: "POST",
    body: form,
  });
}

export async function analyzeFile(file) {
  if (!file) {
    throw new BackendApiError("File is required", 422);
  }

  const contractForm = new FormData();
  contractForm.append("file", file);

  try {
    // Contract format.
    return await fetchWithAuth("/ocr/extract", {
      method: "POST",
      body: contractForm,
    });
  } catch (error) {
    if (!isFallbackStatus(error)) throw error;
  }

  // Legacy route fallback.
  const fallbackForm = new FormData();
  fallbackForm.append("file", file);
  return fetchWithAuth("/analyze", {
    method: "POST",
    body: fallbackForm,
  });
}

export function getBackendBaseUrl() {
  return backendBaseUrl;
}

export async function checkBackendHealth() {
  const start = Date.now();
  const response = await fetch(`${backendBaseUrl}/health`, { method: "GET" });
  const latencyMs = Date.now() - start;

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    throw new BackendApiError(
      extractErrorMessage(payload, `Health check failed (${response.status})`),
      response.status,
      payload,
    );
  }

  return {
    payload,
    latencyMs,
  };
}
