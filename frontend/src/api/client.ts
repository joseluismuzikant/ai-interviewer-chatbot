export const API_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function getErrorMessage(
  response: Response,
  fallbackMessage: string
): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string" && payload.detail.trim().length > 0) {
      return payload.detail;
    }
  } catch {
    // ignore JSON parse errors and fall back to default message
  }
  return `${fallbackMessage} (${response.status})`;
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const fallback = `Request to ${path} failed`;
    throw new Error(await getErrorMessage(response, fallback));
  }
  return response.json() as Promise<T>;
}
