FROM python:3.12-alpine AS build
WORKDIR /app
COPY build.py ./
COPY data ./data
COPY src ./src
COPY media ./media
RUN python3 build.py

FROM caddy:2.8-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
