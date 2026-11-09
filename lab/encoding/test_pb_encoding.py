import os
import zlib
import gzip

PB_PATH = r"C:\Users\cochr\.gemini\antigravity\conversations\1cfae999-9108-4b5e-955e-667dd3eeee89.pb"

with open(PB_PATH, "rb") as f:
    data = f.read(100000)

print(f"Data length: {len(data)}")
print(f"First 32 bytes hex: {data[:32].hex()}")

# Probar zlib
try:
    decomp = zlib.decompress(data)
    print("ZLIB exitoso! Primeros 64 bytes:", decomp[:64])
except Exception as e:
    print(f"ZLIB fallo: {e}")

# Probar gzip
try:
    decomp = gzip.decompress(data)
    print("GZIP exitoso! Primeros 64 bytes:", decomp[:64])
except Exception as e:
    print(f"GZIP fallo: {e}")

# Buscar strings ASCII / UTF-8 dentro de los primeros 100KB
import re
ascii_strings = re.findall(rb'[A-Za-z0-9_ -]{6,}', data[:20000])
print(f"Strings encontrados en los primeros 20KB: {len(ascii_strings)}")
for s in ascii_strings[:10]:
    print(" ", s.decode('ascii', errors='ignore'))

