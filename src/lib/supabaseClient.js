import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    })
  : null;

const AUTH_FLAG_KEY = "campusshield-auth";
const USER_ID_KEY = "campusshield-user-id";
const USER_EMAIL_KEY = "campusshield-user-email";
const USER_NAME_KEY = "campusshield-user-name";

function getNameFromMetadata(user) {
  return user?.user_metadata?.name || user?.user_metadata?.full_name || "";
}

export function cacheAuthenticatedUser(user) {
  if (!user) return;
  localStorage.setItem(AUTH_FLAG_KEY, "true");
  if (user.id) localStorage.setItem(USER_ID_KEY, user.id);
  if (user.email) localStorage.setItem(USER_EMAIL_KEY, user.email);
  const name = getNameFromMetadata(user);
  if (name) localStorage.setItem(USER_NAME_KEY, name);
}

export function clearCachedAuth() {
  localStorage.removeItem(AUTH_FLAG_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(USER_EMAIL_KEY);
  localStorage.removeItem(USER_NAME_KEY);
}

export function getCachedUserId() {
  return localStorage.getItem(USER_ID_KEY) || "";
}

export async function getAccessToken() {
  if (!supabase) return null;
  const { data, error } = await supabase.auth.getSession();
  if (error) return null;
  return data.session?.access_token ?? null;
}
