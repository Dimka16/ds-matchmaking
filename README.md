# DS Matchmaking (Kafka + Flask + Postgres + Socket.IO)

A distributed matchmaking system built with **Flask**, **Kafka**, **Postgres**, and **Socket.IO**.
Players can register/login, join matchmaking queues for different game modes, and receive real-time
match notifications. Workers consume Kafka events and create match sessions stored in Postgres.

---

## Architecture Overview

### Components
- **API (Flask)**
  - Auth (register/login → JWT)
  - Matchmaking endpoints (join/leave queue → publish Kafka events)
  - Sessions endpoints (list/get match sessions)
  - Debug dashboard (`/debug`) and system event log (`/debug/events`)
  - Socket.IO server for real-time notifications

- **Kafka**
  - A topic per game mode (event-driven matchmaking)
  - Messages are published **without a key** (NULL key), allowing Kafka to distribute load across partitions automatically

- **Workers (one per mode)**
  - Each worker belongs to its own **consumer group** (e.g., `solo-workers`)
  - Consumes queue events from its mode’s topic
  - Maintains an **in-memory waiting pool** and runs a matchmaking strategy
  - When a match is formed, it calls the API to create a session in the database

- **Postgres**
  - Stores durable match data:
    - `match_sessions` (session id, mode, created_at)
    - `match_players` (players in each session)

- **Socket.IO**
  - Each client registers into a room: `player:<id>`
  - When a session is created, the API emits `match_found` to each matched player’s room

---

## Kafka Topics and Consumer Groups

Each game mode has its own Kafka topic and worker consumer group:

| Game Mode  | Kafka Topic        | Consumer Group       | Match Type        |
|------------|--------------------|----------------------|-------------------|
| classic    | `match.classic`    | `classic-workers`    | 1v1               |
| solo       | `match.solo`       | `solo-workers`       | 1v1 (stricter)    |
| duo        | `match.duo`        | `duo-workers`        | 2v2               |
| blitz      | `match.blitz`      | `blitz-workers`      | 1v1 (fast)        |
| tournament | `match.tournament` | `tournament-workers` | bracket (8/16/32) |

### Partitioning
Topics are created with multiple partitions (configurable via `KAFKA_TOPIC_PARTITIONS`).
Events are sent with **no key**, so Kafka distributes messages across partitions automatically.

---

## Matchmaking Logic (Strategies)

All modes use **region-based matching**:
- Players are matched only with other players from the **same region**.

### classic (1v1)
- Matches two players in the same region whose ELO difference is within a threshold.
- Balanced + flexible matchmaking.

### solo (1v1 strict)
- Stricter version of classic:
  - smaller ELO threshold
  - players are sorted by ELO and matched as adjacent neighbors if within threshold
- Designed for “fairer” matches.

### duo (2v2)
- Requires 4 players from the same region.
- Forms two teams (2v2) and tries to balance team average/sum ELO.

### blitz (fast 1v1)
- A fast mode focused on minimal wait time:
  - starts with a base ELO threshold
  - after waiting, threshold relaxes over time
  - after too long, it forces a match with the closest available player even if ELO limits would normally fail

### tournament
- Collects players until reaching a bracket size (8/16/32).
- Produces a seeded bracket order (by ELO) and creates a tournament session.

---

## Data Model (Database)

- `match_sessions`
  - `id` (UUID string)
  - `game_mode`
  - `created_at`

- `match_players`
  - `match_id` (FK → match_sessions.id)
  - `player_id`
  - `username`
  - `elo`
  - `region`
  - `seed_order`

---

## Run the Project

```bash
docker compose down -v
docker compose up -d --build
docker compose ps
