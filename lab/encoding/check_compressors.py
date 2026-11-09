import sys

modules = ["zstandard", "lz4", "brotli", "snappy", "cryptography"]
for m in modules:
    try:
        __import__(m)
        print(f"Modulo disponible: {m}")
    except ImportError:
        print(f"No instalado: {m}")

