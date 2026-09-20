#!/bin/sh
set -eu

LOG=/downloads/.yt-dlp.log
PIDFILE=/downloads/.yt-dlp.pid
ARCHIVE=/downloads/.yt-dlp-archive.txt

run() {
  [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null && return 0
  (
    yt-dlp \
      -a /opt/channels.txt \
      --download-archive "$ARCHIVE" \
      --dateafter now-7days \
      --playlist-end 5 \
      --format "bv*[height<=720]+ba/b" \
      --merge-output-format mp4 \
      --output "/downloads/%(channel)s/%(upload_date)s %(title)s [%(id)s].%(ext)s" \
      --embed-thumbnail \
      --embed-metadata \
      --limit-rate 5M -i --newline >> "$LOG" 2>&1
    chown -R 1000:1000 /downloads
  ) &
  echo $! > "$PIDFILE"
}

run

echo "30 5 * * * /bin/sh /opt/dl.sh run" > /var/spool/cron/crontabs/root
chmod 600 /var/spool/cron/crontabs/root
crond -b -c /var/spool/cron/crontabs

tail -f /dev/null