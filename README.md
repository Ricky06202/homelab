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
| `casa2.rumbo` | `8123` | Home Assistant | sí |
| `pedidos.rumbo` | `5055` | Jellyseerr (pendiente) | sí |
| `status.rumbo` | `3010` | Homepage | no |

> Nota: NPM e Immich corren como **Apps nativas de TrueNAS (`ix-*`)**, no por compose propio — por eso no tienen compose en este repo. NPM: el `database.sqlite` (rutas) vive en `/mnt/.ix-apps/app_configs/nginx-proxy-manager/`.

## Servicio → puerto directo (sin proxy, mismo host)

| Servicio | URL directa |
|---|---|
| qBittorrent WebUI | `http://192.168.2.90:8086` (primer login: `admin` + pass temporal del log) |
| Navidrome | `http://192.168.2.90:4533` (primer login: creás el admin) |
| Home Assistant | `http://192.168.2.90:8123` (onboarding al primer arranque) |
| Prowlarr | `http://192.168.2.90:9696` |
| Radarr | `http://192.168.2.90:7878` |
| Sonarr | `http://192.168.2.90:8989` |
| MeTube | `http://192.168.2.90:8085` |
| Homepage | `http://192.168.2.90:3010` |
