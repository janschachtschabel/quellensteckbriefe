# Deployment auf Debian 13 (Docker Compose)

Ein einzelner Container liefert API **und** Frontend samt mitgeliefertem
Datenstand aus. Das Team-Passwort wird **nicht** ins Image gebacken, sondern
beim Start über `.env` gesetzt.

Auf dem Server werden nur **zwei Dateien** gebraucht: `docker-compose.yml`
und `.env` (kopiert aus `.env.example`).

## 1. Docker installieren (Debian 13 „Trixie")

Einfachster Weg über die Debian-Pakete:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
```

> Alternativ die jeweils neueste Docker-Engine aus dem offiziellen Docker-Repo:
> <https://docs.docker.com/engine/install/debian/>

Optional ohne `sudo` arbeiten (danach einmal ab- und wieder anmelden):

```bash
sudo usermod -aG docker $USER
```

## 2. Deploy-Dateien auf den Server bringen

Entweder das Repo klonen …

```bash
git clone https://github.com/janschachtschabel/quellensteckbriefe.git
cd quellensteckbriefe/deploy
```

… oder nur `docker-compose.yml` + `.env.example` aus diesem `deploy/`-Ordner
per `scp` in ein Verzeichnis auf dem Server kopieren.

## 3. Konfigurieren

```bash
cp .env.example .env
nano .env
```

In `.env` eintragen:

| Variable | Bedeutung |
|---|---|
| `IMAGE` | `DEINUSER/quellensteckbriefe:latest` — deinen Docker-Hub-Benutzer einsetzen |
| `QE_TEAM_PASSWORD` | Passwort für die internen Team-Ansichten (frei wählen, geheim halten) |
| `PORT` | Host-Port (Default `8080`) |

> Ist das Docker-Hub-Repo **privat**, vorher einmalig anmelden: `docker login`.

## 4. Starten

```bash
sudo docker compose pull
sudo docker compose up -d
sudo docker compose ps
```

Prüfen:

```bash
curl -s http://localhost:8080/api/stats | head -c 200; echo
```

→ liefert JSON. Im Browser: `http://<SERVER-IP>:8080`

Firewall (falls `ufw` aktiv ist):

```bash
sudo ufw allow 8080/tcp
```

## Betrieb

| Aktion | Befehl |
|---|---|
| Logs ansehen | `sudo docker compose logs -f` |
| Status / Health | `sudo docker compose ps` |
| Aktualisieren | `sudo docker compose pull && sudo docker compose up -d` |
| Stoppen | `sudo docker compose down` |
| Neu starten | `sudo docker compose restart` |

Durch `restart: unless-stopped` + aktivierten Docker-Dienst startet der
Container nach einem Server-Neustart automatisch wieder.

## Hinweise

- **Datenstand:** Das Image enthält `truth.json`. Der Live-Refresh (Team-Button)
  baut die Daten im Container neu, aber **nur bis zum Neustart** (ephemer). Für
  dauerhaft frische Daten das Image regelmäßig neu ziehen (CI baut es bei jedem
  Push auf `main` neu).
- **HTTPS:** Für öffentlichen Betrieb einen Reverse-Proxy (Caddy/nginx/Traefik)
  vor den Container setzen, der TLS terminiert und auf `127.0.0.1:8080` weiterleitet.
- **Passwort-Default:** Ohne gesetztes `QE_TEAM_PASSWORD` nutzt die App
  `wlo-intern` — im Betrieb unbedingt überschreiben.
