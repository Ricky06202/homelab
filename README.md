# Homelab Sanjur — mapa de servicios

> NAS: `192.168.2.90` · DNS interno: AdGuard (rewrites `*.sanjur.internal`)
> Todas las apps viven en el pool `Datos`, contenedores Docker (uid 1000), datos en `config/`/`data/` (excluidos del git — se regeneran al levantar).

## Mapa DNS → puerto (para recrear los proxy hosts en NPM)

| Subdominio (AdGuard rewrite) | Puerto | Servicio | WebSockets en NPM |
|---|---|---|---|
| `casa.rumbo` | `8080` | panel TrueNAS (ix-*) | sí |
| `dns.rumbo` | `80` | AdGuard (rewrites del DNS) | no |
| `fotos.rumbo` | `8080`→Immich (ix-*) | Immich | sí |
| `nube.rumbo` | `8080`→Nextcloud | Nextcloud | no |
| `flix.rumbo` | `8096` | Jellyfin | sí |
| `series.rumbo` | `8989` | Sonarr | no |
| `pelis.rumbo` | `7878` | Radarr | no |
| `indexadores.rumbo` | `9696` | Prowlarr | no |
| `descargas.rumbo` | `8086` | qBittorrent | sí |
| `musica.rumbo` | `4533` | Navidrome | no |
| `musicaarr.rumbo` | `8686` | Lidarr | no |
| `casa2.rumbo` | `8123` | Home Assistant | sí |
| `pedidos.rumbo` | `5055` | Jellyseerr (pendiente) | sí |
| `status.rumbo` | `3010` | Homepage | no |

> Nota: NPM e Immich corren como **Apps nativas de TrueNAS (`ix-*`)**, no por compose propio — por eso no tienen compose en este repo. NPM: el `database.sqlite` (rutas) vive en `/mnt/.ix-apps/app_configs/nginx-proxy-manager/`.

## YouTube offline (`ytdlp/`)

Container `yt-dlp` (imagen `jauderho/yt-dlp`, se auto-actualiza) descarga automáticamente los canales listados en `ytdlp/channels.txt` (editable, va al git). Baja solo los **últimos 7 días** de videos nuevos, máx 5 por canal, ≤720p, a `/mnt/Download/YouTube/<canal>/`. Cron diario a las **05:30**. Para cambiar de canal: editá `channels.txt` y `docker compose up -d` (no hace falta reiniciar el flujo: la corrida próxima lo usa).

> Para **ver** la descarga: Jellyfin ya monta `/mnt/Download/YouTube:/youtube:ro`; solo falta agregar una librería apuntando a `/youtube` en el dashboard de Jellyfin (Jellyfin > Dashboard > Media Libraries > Add).

## Español vs general (`arr-router/`)

Las colecciones están separadas por idioma con carpetas propias:

- Datos: `/mnt/Download/Flix/series` + `peliculas` (general) · `series-espanol` + `peliculas-espanol` (ES)
- Jellyfin: 4 librerías (Series, Series en Español, Películas, Películas en Español) con monitor en tiempo real activado
- Sonarr/Radarr: root folders id 1 = general, id 2 = ES. Al agregar un título se elige la raíz; los releases que Radarr/Sonarr bajan a la general **con audio español** (aunque sea dual) los mueve a la raíz ES `arr-router/router.py` (cron TrueNAS cada hora: `python3 homelab/arr-router/router.py --run`). Detección: mediaInfo de la app + tags de audio vía ffprobe (jellyfin) + nombre de archivo. Dry-run: correr sin `--run`.

## Servicio → puerto directo (sin proxy, mismo host)

| Servicio | URL directa |
|---|---|
| qBittorrent WebUI | `http://192.168.2.90:8086` (primer login: `admin` + pass temporal del log) |
| Navidrome | `http://192.168.2.90:4533` (primer login: creás el admin) |
| Home Assistant | `http://192.168.2.90:8123` (onboarding al primer arranque) |
| Prowlarr | `http://192.168.2.90:9696` |
| Radarr | `http://192.168.2.90:7878` |
| Sonarr | `http://192.168.2.90:8989` |
| Lidarr | `http://192.168.2.90:8686` |

| Homepage | `http://192.168.2.90:3010` |
