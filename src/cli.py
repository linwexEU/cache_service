import json
import sys
import urllib.error
import urllib.request
from typing import Annotated, Any, Optional

from pydantic import (
    Field,
    HttpUrl,
    PositiveInt,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_HOST: HttpUrl = TypeAdapter(HttpUrl).validate_python("http://127.0.0.1:8000")
TIMEOUT_S = 10.0


class CliSettings(BaseSettings):
    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_prog_name="cache-cli",
        cli_shortcuts={
            "host": ["H"],
            "repeat": ["r"],
            "input_source": ["i"],
            "json_input": ["j"],
            "output": ["o"],
        },
        populate_by_name=True,
    )

    host: Annotated[HttpUrl, Field(default=DEFAULT_HOST, description="Server base URL")] = (
        DEFAULT_HOST
    )
    repeat: Annotated[
        PositiveInt, Field(default=1, description="Number of POST+GET iterations")
    ] = 1
    input_source: Annotated[
        Optional[str],
        Field(default=None, alias="input", description='Input file path, or "-" for stdin'),
    ] = None
    json_input: Annotated[
        Optional[str], Field(default=None, alias="json", description="Inline JSON payload")
    ] = None
    output: Annotated[
        str, Field(default="-", description='Output file path, or "-" for stdout')
    ] = "-"

    @field_validator("host", mode="before")
    @classmethod
    def _strip_trailing_slash(cls, v: Any) -> Any:
        """Normalize the base URL so '{host}/payload' never gets a double slash."""
        return v.rstrip("/") if isinstance(v, str) else v

    @model_validator(mode="after")
    def _require_exactly_one_source(self) -> "CliSettings":
        """Fail fast on ambiguous input instead of guessing which source wins."""
        if bool(self.input_source) == bool(self.json_input):
            raise ValueError("provide exactly one of --input FILE|- or --json JSON")
        return self


def parse_cli_settings(argv: list[str] | None = None) -> CliSettings:
    """Parse argv through Pydantic so all sanitizing lives in CliSettings, not argparse code."""
    return CliSettings(_cli_parse_args=argv)  # type: ignore


def _read_text(source: str) -> str:
    """'-' reads stdin so the CLI composes in shell pipes; otherwise read the file."""
    if source == "-":
        return sys.stdin.read()
    with open(source, "r", encoding="utf-8") as f:
        return f.read()


def load_payload(settings: CliSettings) -> dict[str, list[str]]:
    """Load and normalize the payload; accept task keys (list_1/2) and server keys alike."""
    raw = (
        settings.json_input
        if settings.json_input is not None
        else _read_text(settings.input_source or "")
    )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON payload: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("payload must be a JSON object")

    list_1 = data.get("list_1", data.get("input_lst1"))
    list_2 = data.get("list_2", data.get("input_lst2"))

    if not isinstance(list_1, list) or not isinstance(list_2, list):
        raise ValueError('payload must contain "input_lst1"/"input_lst2" arrays')

    if not all(isinstance(s, str) for s in list_1 + list_2):
        raise ValueError("payload lists must contain only strings")

    return {"input_lst1": list_1, "input_lst2": list_2}


def _request_json(method: str, url: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Minimal JSON client on stdlib urllib, so the CLI needs no HTTP dependency."""
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {url} -> HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"cannot reach {url}: {e.reason}") from e


def run_once(host: str, payload: dict[str, list[str]]) -> dict[str, Any]:
    """One POST-then-GET round trip, mirroring how a client actually uses the service."""
    created = _request_json("POST", f"{host}/payload", payload)
    payload_id = created.get("created_id", created.get("id"))

    if payload_id is None:
        raise RuntimeError(f"POST /payload returned no id: {created}")

    fetched = _request_json("GET", f"{host}/payload/{payload_id}")

    return {"id": payload_id, "output": fetched.get("output")}


def write_output(settings: CliSettings, results: list[dict[str, Any]]) -> None:
    """Single object for one iteration, array for many — stdout stays machine-readable."""
    text = json.dumps(results[0] if len(results) == 1 else results, ensure_ascii=False, indent=2)
    if settings.output == "-":
        print(text)
    else:
        with open(settings.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint; returns exit codes (0/1/2) instead of raising, for shell use."""
    try:
        settings = parse_cli_settings(argv)
    except ValidationError as e:
        print(f"cache-cli: argument error:\n{e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"cache-cli: argument error: {e}", file=sys.stderr)
        return 2
    try:
        payload = load_payload(settings)
    except (ValueError, OSError) as e:
        print(f"cache-cli: input error: {e}", file=sys.stderr)
        return 1
    host = str(settings.host).rstrip("/")
    results: list[dict[str, Any]] = []
    try:
        for i in range(settings.repeat):
            result = run_once(host, payload)
            results.append(result)
            print(f"[{i + 1}/{settings.repeat}] id={result['id']}", file=sys.stderr)
        write_output(settings, results)
    except (RuntimeError, OSError) as e:
        print(f"cache-cli: request failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
