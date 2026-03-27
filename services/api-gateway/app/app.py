from email.mime import base
import os
from os import path
from urllib.parse import urljoin

import requests
from flask import Flask, Response, request


def create_app() -> Flask:
    import config  

    app = Flask(__name__)
    app.config.from_object(config.get_config())

    def _service_base_for_path(path: str) -> str | None:
        p = path.lstrip("/")
        if p.startswith("auth") or p.startswith("users"):
            return app.config["IDENTITY_SERVICE_URL"]
        if p.startswith("workouts"):
            return app.config["WORKOUT_SERVICE_URL"]
        if p.startswith("wgroups"):
            return app.config["WGROUPS_SERVICE_URL"]
        if p.startswith("performance"):
            return app.config["PERFORMANCE_SERVICE_URL"]
        return None

    @app.after_request
    def add_cors_headers(resp: Response):
        allow = (app.config.get("CORS_ALLOW_ORIGINS") or "").strip()
        if allow:
            origin = request.headers.get("Origin")
            allowed = [o.strip() for o in allow.split(",") if o.strip()]
            if origin and (origin in allowed or "*" in allowed):
                resp.headers["Access-Control-Allow-Origin"] = origin if origin != "null" else "*"
                resp.headers["Vary"] = "Origin"
                resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
                resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        return resp

    @app.route("/prbreaker/health", methods=["GET"])
    def health():
        return {"status": "ok", "service": "api-gateway"}

    @app.route("/prbreaker/", defaults={"path": ""}, methods=["GET"])
    def root(path: str):
        return {"status": "ok", "message": "API Gateway running"}

    @app.route("/prbreaker/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    def proxy(path: str):
        base = _service_base_for_path(path)
        if base is None:
            return {"success": False, "message": "Unknown route", "data": {}}, 404

        target = urljoin(base.rstrip("/") + "/", path)
        # Remove "performance/" prefix before forwarding
        # forward_path = path.split("/", 1)[1] if "/" in path else ""

        # target = urljoin(base.rstrip("/") + "/", forward_path)
        # Forward headers (keep Authorization, Content-Type, etc.)
        headers = {}
        for k, v in request.headers.items():
            lk = k.lower()
            if lk in ("host", "content-length", "connection"):
                continue
            headers[k] = v

        try:
            resp = requests.request(
                method=request.method,
                url=target,
                params=request.args,
                headers=headers,
                data=request.get_data(),
                cookies=request.cookies,
                timeout=15,
                allow_redirects=False,
            )
        except requests.RequestException:
            return {"success": False, "message": "Upstream service unavailable", "data": {}}, 502

        excluded = {"content-encoding", "transfer-encoding", "connection", "content-length"}
        out_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]

        return Response(resp.content, status=resp.status_code, headers=out_headers)

    return app


def main():
    app = create_app()
    port = int(app.config.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

