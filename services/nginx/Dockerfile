FROM nginx:1.24-alpine

# Nginx-Konfiguration kopieren
COPY nginx.conf /etc/nginx/nginx.conf

# Log-Verzeichnis erstellen
RUN mkdir -p /var/log/nginx

# Berechtigungen setzen
RUN chown -R nginx:nginx /var/log/nginx

# Health Check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80 