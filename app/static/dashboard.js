const $ = (id) => document.getElementById(id);

const apiOut = $("apiOut");
const authStatus = $("authStatus");

function logApi(obj) {
  apiOut.textContent = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
}

function logEvent(line) {
  const el = $("eventsLog");
  el.textContent += line + "\n";
  el.scrollTop = el.scrollHeight;
}

function getToken() {
  return localStorage.getItem("mm_token") || "";
}

function setToken(t) {
  localStorage.setItem("mm_token", t || "");
  $("token").value = t || "";
  refreshAuthBadge();
}

function parseJwt(token) {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decodeURIComponent(escape(json)));
  } catch {
    return null;
  }
}

function refreshAuthBadge() {
  const t = getToken();
  const claims = t ? parseJwt(t) : null;
  if (claims?.username) {
    authStatus.className = "badge text-bg-success";
    authStatus.textContent = `Logged in as ${claims.username} (id=${claims.sub})`;
    $("btnLogout").disabled = false;
  } else {
    authStatus.className = "badge text-bg-secondary";
    authStatus.textContent = "Not logged in";
    $("btnLogout").disabled = true;
  }
}

async function apiFetch(path, { method="GET", body=null } = {}) {
  const headers = { "Content-Type": "application/json" };
  const t = getToken();
  if (t) headers["Authorization"] = `Bearer ${t}`;

  const res = await fetch(path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null
  });

  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  if (!res.ok) throw { status: res.status, data };
  return data;
}

// --- AUTH ---
$("btnRegister").addEventListener("click", async () => {
  try {
    const username = $("username").value.trim();
    const password = $("password").value;
    const data = await apiFetch("/auth/register", { method: "POST", body: { username, password } });
    logApi(data);
  } catch (e) { logApi(e); }
});

$("btnLogin").addEventListener("click", async () => {
  try {
    const username = $("username").value.trim();
    const password = $("password").value;
    const data = await apiFetch("/auth/login", { method: "POST", body: { username, password } });
    if (data?.token) setToken(data.token);
    logApi(data);
  } catch (e) { logApi(e); }
});

$("btnLogout").addEventListener("click", () => {
  setToken("");
  logApi({ status: "ok", message: "Logged out (token cleared in browser)" });
});

// --- MATCHMAKING ---
$("btnJoin").addEventListener("click", async () => {
  try {
    const body = {
      game_mode: $("gameMode").value,
      elo: Number($("elo").value || 0),
      region: $("region").value || ""
    };
    const data = await apiFetch("/matchmaking/join", { method: "POST", body });
    logApi(data);
  } catch (e) { logApi(e); }
});

$("btnLeave").addEventListener("click", async () => {
  try {
    const body = { game_mode: $("gameMode").value };
    const data = await apiFetch("/matchmaking/leave", { method: "POST", body });
    logApi(data);
  } catch (e) { logApi(e); }
});

// --- SESSIONS ---
function getSessionId(s) {
  return s?.id ?? s?.match_id ?? s?.session_id ?? s?.sessionId ?? null;
}

function getSessionMode(s) {
  return s?.game_mode ?? s?.mode ?? s?.gameMode ?? "";
}

function getSessionCreatedAt(s) {
  return s?.created_at ?? s?.createdAt ?? s?.timestamp ?? "";
}

function renderSessions(list) {
  const container = $("sessionsList");
  container.innerHTML = "";

  if (!Array.isArray(list) || list.length === 0) {
    container.innerHTML = `<div class="text-muted small">No sessions found (or not authorized).</div>`;
    return;
  }

  for (const s of list) {
    const sid = getSessionId(s);
    const mode = getSessionMode(s);
    const created = getSessionCreatedAt(s);

    const a = document.createElement("button");
    a.type = "button";
    a.className = "list-group-item list-group-item-action";
    a.innerHTML = `<div class="d-flex justify-content-between">
      <span class="font-monospace">${sid ?? "(missing id)"}</span>
      <span class="badge text-bg-light">${mode}</span>
    </div>
    <div class="text-muted small">${created}</div>`;

    a.addEventListener("click", () => {
      if (!sid) {
        logApi({ status: "error", error: "Session object has no id field", session: s });
        return;
      }
      $("sessionId").value = sid;
    });

    container.appendChild(a);
  }
}

$("btnRefreshSessions").addEventListener("click", async () => {
  try {
    const data = await apiFetch("/sessions", { method: "GET" });
    renderSessions(data.sessions || data);
    logApi(data);
  } catch (e) { logApi(e); }
});

$("btnGetSession").addEventListener("click", async () => {
  try {
    const id = $("sessionId").value.trim();
    if (!id || id === "undefined" || id === "null") {
      logApi({ status: "error", error: "Invalid session id. Select a valid session from the list." });
      return;
    }
    const data = await apiFetch(`/sessions/${encodeURIComponent(id)}`, { method: "GET" });
    $("sessionDetails").textContent = JSON.stringify(data, null, 2);
    logApi(data);
  } catch (e) { logApi(e); }
});

// --- SYSTEM EVENTS ---
async function refreshSystemEvents() {
  try {
    const data = await apiFetch("/debug/events?limit=50");
    $("systemEvents").textContent = JSON.stringify(data.events || data, null, 2);
    logApi(data);
  } catch (e) { logApi(e); }
}
$("btnRefreshEvents")?.addEventListener("click", refreshSystemEvents);

// --- SOCKET.IO ---
let socket = null;

$("btnConnect").addEventListener("click", () => {
  if (socket?.connected) {
    logEvent("Already connected.");
    return;
  }

  socket = io({ autoConnect: true });
  socket.on("connect", () => logEvent(`socket connected: ${socket.id}`));
  socket.on("disconnect", () => logEvent("socket disconnected"));

  socket.on("registered", (msg) => logEvent("registered: " + JSON.stringify(msg)));
  socket.on("match_found", (msg) => logEvent("match_found: " + JSON.stringify(msg, null, 2)));
});

$("btnRegisterSocket").addEventListener("click", () => {
  if (!socket?.connected) {
    logEvent("Socket not connected. Click Connect first.");
    return;
  }
  const t = getToken();
  const claims = t ? parseJwt(t) : null;
  const pid = claims?.sub ? Number(claims.sub) : null;
  if (!pid) {
    logEvent("No valid token / player id found. Login first.");
    return;
  }
  socket.emit("register_player", { player_id: pid });
  logEvent(`register_player emitted for player_id=${pid}`);
});

// init
$("token").value = getToken();
refreshAuthBadge();
