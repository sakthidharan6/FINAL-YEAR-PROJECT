import os
import sys

files = [
    "backend/__init__.py",
    "backend/main.py",
    "backend/data_processor.py",
    "backend/model_service.py"
]

for f in files:
    print(f"Checking {f}...", flush=True)
    try:
        with open(f, 'rb') as f_obj:
            content_bytes = f_obj.read()
        
        # Try decode
        content = content_bytes.decode('utf-8')
        print(f"{f}: OK, {len(content)} chars", flush=True)
    except Exception as e:
        print(f"{f}: FAILED - {e}", flush=True)
