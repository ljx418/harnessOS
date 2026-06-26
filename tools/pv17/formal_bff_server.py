from __future__ import annotations

import os
from pathlib import Path

from apps.api import create_app
from tools.pv17.reference_seed import create_seeded_gateway


runtime_root = Path(os.environ.get("PV17_RUNTIME_ROOT", "/tmp/harnessos-pv17-runtime")).resolve()
runtime_root.mkdir(parents=True, exist_ok=True)
gateway_service, seeded_reference = create_seeded_gateway(runtime_root)
app = create_app(gateway_service=gateway_service)
