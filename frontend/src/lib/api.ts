const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchDashboard() {
  const res = await fetch(`${API_URL}/api/dashboard`);
  if (!res.ok) throw new Error(`Dashboard fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchSpots() {
  const res = await fetch(`${API_URL}/api/spots`);
  return res.json();
}

export async function subscribe(email: string, cadence: string) {
  const res = await fetch(`${API_URL}/api/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, cadence }),
  });
  return res.json();
}

export async function submitFeedback(
  type: string,
  text: string,
  email?: string
) {
  const res = await fetch(`${API_URL}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, text, email: email || "" }),
  });
  return res.json();
}

export async function adminLogin(password: string) {
  const res = await fetch(`${API_URL}/api/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  if (!res.ok) throw new Error("Invalid password");
  return res.json();
}

export async function getSubscribers(token: string) {
  const res = await fetch(`${API_URL}/api/admin/subscribers`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function deleteSubscriber(email: string, token: string) {
  const res = await fetch(`${API_URL}/api/admin/subscribers/${email}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function getFeedback(token: string) {
  const res = await fetch(`${API_URL}/api/admin/feedback`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function sendTestBriefing(
  email: string,
  type: string,
  token: string
) {
  const res = await fetch(`${API_URL}/api/admin/test-briefing`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ email, type }),
  });
  return res.json();
}

export async function sendTestWelcome(
  email: string,
  token: string
) {
  const res = await fetch(`${API_URL}/api/admin/test-email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ email }),
  });
  return res.json();
}
