import asyncio
import signal
import sys
from pathlib import Path

import uvicorn


def main() -> None:
    server_dir = Path(__file__).resolve().parents[1] / "server"
    sys.path.insert(0, str(server_dir))
    config = uvicorn.Config(
        "app:app",
        host="0.0.0.0",
        port=26472,
        log_level="info",
    )
    server = uvicorn.Server(config)
    server.install_signal_handlers = False

    def _handle_signal(_signum, _frame) -> None:
        server.should_exit = True

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        asyncio.run(server.serve())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass


if __name__ == "__main__":
    main()
