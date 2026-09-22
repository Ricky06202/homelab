#!/usr/bin/env python3
"""arr-router: rutea medios a la carpeta en espanol segun el audio real.

Regla: si un item contiene audio espanol/latino (aunque sea dual) va a
/flix/peliculas-espanol o /flix/series-espanol. Items sin audio espanol
(incl. japones, aleman, dde etc.) quedan donde estan.

- Contenido gestionado por Radarr/Sonarr: se mueve via su API (moveFiles=true).
- Archivos sueltos (no gestionados): mv directo.
Deteccion: mediaInfo de la app + ffprobe (tags reales de audio) + nombre.
Correr sin args para dry-run; --run aplica.
"""
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

DRY = "--run" not in sys.argv
API_BASE = "http://192.168.2.90"
JELLY_HOST = "/mnt/Download/Flix"
SPANISH_NAME = re.compile(r"spanish|latino|espa[nñ]ol|castellan", re.I)
SPANI_TAGS = ("spa", "lat", "cast")
VIDEOS = (".mkv", ".mp4", ".avi", ".m4v", ".mov", ".webm")


def api(app, port, path, key, body=None):
    req = urllib.request.Request(f"{API_BASE}:{port}{path}", headers={"X-Api-Key": key})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
        req.get_method = lambda: "PUT"
    with urllib.request.urlopen(req, data, timeout=60) as r:
        raw = r.read()
        return json.loads(raw) if raw else None


def ffprobe_audio(host_path):
    """Tags de idioma de las pistas de audio, ej. 'spa,eng,' o ','.

    host_path: ruta REAL en /mnt/... ; se traduce al mount de jellyfin."""
    p = host_path
    for host_p, in_p in (
        (f"{JELLY_HOST}/peliculas-espanol", "/peliculas-espanol"),
        (f"{JELLY_HOST}/peliculas", "/peliculas"),
        (f"{JELLY_HOST}/series-espanol", "/series-espanol"),
        (f"{JELLY_HOST}/series", "/series"),
    ):
        if p.startswith(host_p):
            p = in_p + p[len(host_p):]
            break
    r = subprocess.run(
        ["sudo", "-n", "docker", "exec", "jellyfin", "/usr/lib/jellyfin-ffmpeg/ffprobe",
         "-v", "quiet", "-select_streams", "a",
         "-show_entries", "stream_tags=language", "-of", "csv=p=0", p],
        capture_output=True, text=True, timeout=60)
    return r.stdout.lower()


def is_spanish(display_name, *hints):
    hay = ",".join(h or "" for h in hints).lower()
    hay = hay.replace("spanish", "spa").replace("español", "spa")
    if any(t in hay for t in SPANI_TAGS):
        return True
    if "eng" in hay or "jpn" in hay or "dut" in hay or "ger" in hay:
        return False
    return bool(SPANISH_NAME.search(display_name))


def main():
    moves = 0

    # ---------- Radarr: pelis gestionadas ----------
    rkey = api_key("/mnt/Datos/Home/amado/homelab/radarr/config/config.xml")
    managed_paths = set()
    for m in api("radarr", 7878, "/api/v3/movie", rkey):
        managed_paths.add(m["path"])
        if not m.get("hasFile") or not m["path"].startswith("/peliculas/"):
            continue
        f = api("radarr", 7878, f"/api/v3/moviefile/{m['movieFileId']}?includeMediaInfo=true", rkey)
        host_file = f"{JELLY_HOST}{f['path'][len('/peliculas'):]}"
        tags = ffprobe_audio(host_file)
        if not is_spanish(m["title"], (f.get("mediaInfo") or {}).get("audioLanguages"),
                          f["path"].rsplit("/", 1)[-1], tags):
            continue
        m["path"] = "/flix/peliculas-espanol" + m["path"][len("/peliculas"):]
        m["rootFolderPath"] = "/flix/peliculas-espanol"
        print(f"[radarr] {m['title']} -> {m['path']}  (tags: {tags.strip() or '?'})")
        if not DRY:
            api("radarr", 7878, f"/api/v3/movie/{m['id']}?moveFiles=true", rkey, m)
        moves += 1

    # ---------- Radarr: archivos sueltos en /peliculas ----------
    dst = Path(f"{JELLY_HOST}/peliculas-espanol")
    for p in sorted(Path(f"{JELLY_HOST}/peliculas").iterdir()):
        if p.is_dir() or p.suffix.lower() not in VIDEOS:
            continue
        if is_spanish(p.name, p.name, ffprobe_audio(str(p))):
            print(f"[suelto] {p.name} -> {dst}")
            if not DRY:
                shutil.move(str(p), str(dst / p.name))
            moves += 1

    # ---------- Sonarr: series gestionadas ----------
    skey = api_key("/mnt/Datos/Home/amado/homelab/sonarr/config/config.xml")
    for s in api("sonarr", 8989, "/api/v3/series", skey):
        if not s["path"].startswith("/series/"):
            continue
        files = [x for x in api("sonarr", 8989, f"/api/v3/episodefile?seriesId={s['id']}", skey)
                 if x.get("mediaInfo")]
        if not files:
            continue
        sample = files[0]
        host_file = f"{JELLY_HOST}{sample['path'][len('/series'):]}"
        tags = ffprobe_audio(host_file)
        info = sample.get("mediaInfo") or {}
        if not is_spanish(s["title"], info.get("audioLanguages"),
                          sample["path"].rsplit("/", 1)[-1], tags):
            continue
        s["path"] = "/flix/series-espanol" + s["path"][len("/series"):]
        s["rootFolderId"] = 2
        print(f"[sonarr] {s['title']} -> {s['path']}  (tags: {tags.strip() or '?'})")
        if not DRY:
            api("sonarr", 8989, f"/api/v3/series/{s['id']}?moveFiles=true", skey, s)
        moves += 1

    print("DRY-RUN: nada movido." if DRY else f"listo: {moves} movido(s)")


def api_key(path):
    m = re.search(r"<ApiKey>([^<]+)</ApiKey>", open(path).read())
    return m.group(1)


if __name__ == "__main__":
    main()
