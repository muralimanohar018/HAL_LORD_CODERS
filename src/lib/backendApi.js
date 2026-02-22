import { getAccessToken, refreshAccessToken } from "./supabaseClient";

const backendBaseUrl = (import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
const requestTimeoutMs = Number(import.meta.env.VITE_BACKEND_TIMEOUT_MS || 20000);

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

function buildHeaders(initHeaders, token) {
  const headers = new Headers(initHeaders || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return headers;
}

async function parsePayload(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

async function doFetch(path, init, token) {
  const controller = new AbortController();
  const timeoutHandle = setTimeout(() => controller.abort(), requestTimeoutMs);

  try {
    return await fetch(`${backendBaseUrl}${path}`, {
      ...init,
      headers: buildHeaders(init.headers, token),
      signal: controller.signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new BackendApiError("Backend connectivity issue", 0);
    }
    throw error;
  } finally {
    clearTimeout(timeoutHandle);
  }
}

async function fetchWithAuth(path, init = {}) {
  const token = await getAccessToken();
  let response;
  try {
    response = await doFetch(path, init, token);
  } catch (error) {
    if (error instanceof BackendApiError) {
      throw error;
    }
    throw new BackendApiError("Backend connectivity issue", 0);
  }

  if (response.status === 401) {
    const refreshedToken = await refreshAccessToken();
    if (refreshedToken) {
      try {
        response = await doFetch(path, init, refreshedToken);
      } catch (error) {
        if (error instanceof BackendApiError) {
          throw error;
        }
        throw new BackendApiError("Backend connectivity issue", 0);
      }
    }
  }

  const payload = await parsePayload(response);

  if (!response.ok) {
    if (response.status === 401) {
      throw new BackendApiError("Unauthorized. Please log in again.", 401, payload);
    }
    const defaultMessage = `Backend request failed (${response.status})`;
    const message = extractErrorMessage(payload, defaultMessage);
    throw new BackendApiError(message, response.status, payload);
  }

  return payload;
}

async function fetchWithoutAuth(path, init = {}) {
  try {
    const response = await doFetch(path, init, null);
    const payload = await parsePayload(response);
    if (!response.ok) {
      throw new BackendApiError(
        extractErrorMessage(payload, `Backend request failed (${response.status})`),
        response.status,
        payload,
      );
    }
    return payload;
  } catch (error) {
    if (error instanceof BackendApiError) {
      throw error;
    }
    throw new BackendApiError("Backend connectivity issue", 0);
  }
}

export async function analyzeText(text) {
  const trimmed = String(text || "").trim();
  if (!trimmed) {
    throw new BackendApiError("Text is required", 422);
  }

  return fetchWithAuth("/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: trimmed }),
  });
}

export async function analyzeFile(file) {
  if (!file) {
    throw new BackendApiError("File is required", 422);
  }

  const contractForm = new FormData();
  contractForm.append("file", file);

  return fetchWithAuth("/ocr/extract", {
    method: "POST",
    body: contractForm,
  });
}

export function getBackendBaseUrl() {
  return backendBaseUrl;
}

export async function checkBackendHealth() {
  const start = Date.now();
  const payload = await fetchWithoutAuth("/health", { method: "GET" });
  const latencyMs = Date.now() - start;

  return {
    payload,
    latencyMs,
  };
}

export async function fetchScanHistory(limit = 100) {
  const safeLimit = Number.isFinite(limit) ? Math.max(1, Math.min(500, Math.round(limit))) : 100;
  return fetchWithAuth(`/history?limit=${safeLimit}`, {
    method: "GET",
  });
}
