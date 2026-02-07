from __future__ import annotations

import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


def _load_env() -> None:
    env_path = os.getenv("ENV_PATH")
    if env_path:
        load_dotenv(dotenv_path=env_path, override=False)
        return

    here = Path(__file__).resolve().parent
    candidate = here / ".env"
    if candidate.exists():
        load_dotenv(dotenv_path=str(candidate), override=False)
        return

    cwd_candidate = Path.cwd() / ".env"
    if cwd_candidate.exists():
        load_dotenv(dotenv_path=str(cwd_candidate), override=False)


_load_env()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8088").rstrip("/")
SOCKET_URL = os.getenv("SOCKET_URL", BASE_URL).rstrip("/")

REGISTER_PATH = os.getenv("REGISTER_PATH", "/auth/register")
LOGIN_PATH = os.getenv("LOGIN_PATH", "/auth/login")
JOIN_PATH = os.getenv("JOIN_PATH", "/matchmaking/join")

TOKEN_KEY = os.getenv("TOKEN_KEY", "access_token")

SOCKET_REGISTER_EVENT = os.getenv("SOCKET_REGISTER_EVENT", "register_player")
SOCKET_MATCH_FOUND_EVENT = os.getenv("SOCKET_MATCH_FOUND_EVENT", "match_found")

USERNAME_PREFIX = os.getenv("USERNAME_PREFIX", "demo")
PASSWORD_PREFIX = os.getenv("PASSWORD_PREFIX", "Pass123!")

REGION = os.getenv("REGION", "EU")
JOIN_DELAY_MS = int(os.getenv("JOIN_DELAY_MS", "30"))
CONNECT_SOCKETS = os.getenv("CONNECT_SOCKETS", "1") == "1"

N_CLASSIC = int(os.getenv("N_CLASSIC", "20"))
N_SOLO = int(os.getenv("N_SOLO", "10"))
N_DUO = int(os.getenv("N_DUO", "12"))
N_BLITZ = int(os.getenv("N_BLITZ", "10"))
N_TOURNAMENT = int(os.getenv("N_TOURNAMENT", "8"))

ELO_MIN = int(os.getenv("ELO_MIN", "1200"))
ELO_MAX = int(os.getenv("ELO_MAX", "1400"))

CONCURRENCY = int(os.getenv("CONCURRENCY", "10"))

SESSION = requests.Session()


def _url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return f"{BASE_URL}{path}"


def _post_json(path: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> requests.Response:
    return SESSION.post(_url(path), json=payload, headers=headers, timeout=25)


def _ensure_registered(username: str, password: str) -> None:
    r = _post_json(REGISTER_PATH, {"username": username, "password": password})
    if r.status_code in (200, 201):
        return
    if r.status_code in (400, 409):
        return
    r.raise_for_status()


def _login(username: str, password: str) -> str:
    r = _post_json(LOGIN_PATH, {"username": username, "password": password})
    r.raise_for_status()
    data = r.json()
    token = data.get(TOKEN_KEY)
    if not token:
        raise RuntimeError(
            f"Login response missing token key '{TOKEN_KEY}'. Got keys: {list(data.keys())}. "
            f"Set TOKEN_KEY in .env if different."
        )
    return token


def _join(token: str, mode: str, region: str, elo: int) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    r = _post_json(JOIN_PATH, {"game_mode": mode, "region": region, "elo": elo}, headers=headers)
    r.raise_for_status()
    if not r.content:
        return {"ok": True}
    try:
        return r.json()
    except Exception:
        return {"ok": True, "raw": r.text}


def _make_user(i: int) -> tuple[str, str]:
    return f"{USERNAME_PREFIX}{i}", f"{PASSWORD_PREFIX}{i}"


def _plan_users() -> list[tuple[str, str]]:
    total = N_CLASSIC + N_SOLO + N_DUO + N_BLITZ + N_TOURNAMENT
    return [_make_user(i) for i in range(1, total + 1)]


def _elo_clustered() -> int:
    return random.randint(ELO_MIN, ELO_MAX)


def _socket_available() -> bool:
    try:
        import socketio  # noqa: F401
        from importlib.metadata import version as pkg_version

        v = pkg_version("python-socketio")
        major = int(v.split(".", 1)[0])
        return major >= 4
    except Exception:
        return False


def _connect_socket(player_id: str):
    import socketio

    try:
        v = getattr(socketio, "__version__", "unknown")
        if v != "unknown":
            major = int(str(v).split(".", 1)[0])
            if major < 4:
                raise RuntimeError(f"Wrong socketio version imported: {v}. Need python-socketio (v4+).")
    except Exception:
        pass

    sio = socketio.Client(reconnection=True, logger=False, engineio_logger=False)

    @sio.event
    def connect():
        sio.emit(SOCKET_REGISTER_EVENT, {"player_id": player_id})

    @sio.on(SOCKET_MATCH_FOUND_EVENT)
    def on_match_found(data):
        print(f"[MATCH_FOUND] player={player_id} data={data}")

    sio.connect(SOCKET_URL, transports=["websocket", "polling"])
    return sio


def _emit_for_mode(tokens: dict[str, str], users: list[str], mode: str) -> None:
    for u in users:
        elo = _elo_clustered()
        resp = _join(tokens[u], mode, REGION, elo)
        handled_by = resp.get("handled_by")
        if handled_by:
            print(f"[JOIN] user={u} mode={mode} region={REGION} elo={elo} handled_by={handled_by}")
        else:
            print(f"[JOIN] user={u} mode={mode} region={REGION} elo={elo}")
        if JOIN_DELAY_MS > 0:
            time.sleep(JOIN_DELAY_MS / 1000.0)


def main() -> None:
    print(f"BASE_URL={BASE_URL}")
    print(f"SOCKET_URL={SOCKET_URL}")
    print(f"REGISTER={_url(REGISTER_PATH)}")
    print(f"LOGIN={_url(LOGIN_PATH)} TOKEN_KEY={TOKEN_KEY}")
    print(f"JOIN={_url(JOIN_PATH)}")
    print(f"REGION={REGION} ELO=[{ELO_MIN},{ELO_MAX}] JOIN_DELAY_MS={JOIN_DELAY_MS}")
    print(f"Counts classic={N_CLASSIC} solo={N_SOLO} duo={N_DUO} blitz={N_BLITZ} tournament={N_TOURNAMENT}")
    print(f"CONCURRENCY={CONCURRENCY} CONNECT_SOCKETS={CONNECT_SOCKETS}")

    users = _plan_users()
    user_names = [u for (u, _) in users]

    tokens: dict[str, str] = {}
    sockets = []

    def _reg_login(pair: tuple[str, str]) -> tuple[str, str]:
        u, p = pair
        _ensure_registered(u, p)
        tok = _login(u, p)
        return u, tok

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = [ex.submit(_reg_login, pair) for pair in users]
        for fut in as_completed(futures):
            u, tok = fut.result()
            tokens[u] = tok

    if CONNECT_SOCKETS:
        if not _socket_available():
            print("[SOCKET] python-socketio not usable. Set CONNECT_SOCKETS=0 or reinstall: pip install -U "
                  "\"python-socketio[client]\"")
        else:
            for u in user_names:
                try:
                    sockets.append(_connect_socket(u))
                except Exception as e:
                    print(f"[SOCKET_FAIL] user={u} err={e}")

    idx = 0
    classic_users = user_names[idx: idx + N_CLASSIC]
    idx += N_CLASSIC
    solo_users = user_names[idx: idx + N_SOLO]
    idx += N_SOLO
    duo_users = user_names[idx: idx + N_DUO]
    idx += N_DUO
    blitz_users = user_names[idx: idx + N_BLITZ]
    idx += N_BLITZ
    tournament_users = user_names[idx: idx + N_TOURNAMENT]

    random.shuffle(classic_users)
    random.shuffle(solo_users)
    random.shuffle(duo_users)
    random.shuffle(blitz_users)
    random.shuffle(tournament_users)

    if len(classic_users) % 2 != 0:
        classic_users = classic_users[:-1]
    if len(solo_users) % 2 != 0:
        solo_users = solo_users[:-1]
    if len(blitz_users) % 2 != 0:
        blitz_users = blitz_users[:-1]
    if len(duo_users) % 4 != 0:
        duo_users = duo_users[: len(duo_users) - (len(duo_users) % 4)]

    print(
        f"Planned joins: classic={len(classic_users)} solo={len(solo_users)} duo={len(duo_users)} blitz={len(blitz_users)} tournament={len(tournament_users)}")

    try:
        _emit_for_mode(tokens, classic_users, "classic")
        _emit_for_mode(tokens, solo_users, "solo")
        _emit_for_mode(tokens, duo_users, "duo")
        _emit_for_mode(tokens, blitz_users, "blitz")
        _emit_for_mode(tokens, tournament_users, "tournament")

        print("All joins sent. Keep this running to see MATCH_FOUND events (if sockets connected). Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        for s in sockets:
            try:
                s.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    main()
