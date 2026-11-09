import os
import shutil

BASE_DIR = r"c:\xampp\htdocs\stock_productos\references\antygravity_adapter"

# Definir carpetas de destino
LAB_DIR = os.path.join(BASE_DIR, "lab")
LAB_DB = os.path.join(LAB_DIR, "database")
LAB_ENCODING = os.path.join(LAB_DIR, "encoding")
LAB_RPC_DISCOVERY = os.path.join(LAB_DIR, "rpc_discovery")
LAB_RPC_TESTS = os.path.join(LAB_DIR, "rpc_tests")

for d in [LAB_DB, LAB_ENCODING, LAB_RPC_DISCOVERY, LAB_RPC_TESTS]:
    os.makedirs(d, exist_ok=True)

# Mapeo exacto de cada archivo a su subcarpeta
FILE_MAPPING = {
    # 1. Base de datos y SQLite
    "inspect_db.py": LAB_DB,
    "inspect_sample_db.py": LAB_DB,
    "inspect_vscdb.py": LAB_DB,
    "list_all_convs.py": LAB_DB,
    "find_fts_mention.py": LAB_DB,
    "read_fts_chunk0.py": LAB_DB,
    "inspect_all_chunks.py": LAB_DB,

    # 2. Análisis de binarios, compresión y PB
    "check_compressors.py": LAB_ENCODING,
    "check_pb_type.py": LAB_ENCODING,
    "check_inactive_pb.py": LAB_ENCODING,
    "test_pb_encoding.py": LAB_ENCODING,
    "inspect_pb.py": LAB_ENCODING,
    "scan_agy_exe.py": LAB_ENCODING,

    # 3. Descubrimiento de endpoints en código fuente
    "find_service_methods.py": LAB_RPC_DISCOVERY,
    "find_rpc_endpoints.py": LAB_RPC_DISCOVERY,
    "find_rpc_calls.py": LAB_RPC_DISCOVERY,
    "find_service_name.py": LAB_RPC_DISCOVERY,
    "find_service_paths.py": LAB_RPC_DISCOVERY,
    "find_lss.py": LAB_RPC_DISCOVERY,
    "find_wh.py": LAB_RPC_DISCOVERY,
    "find_pkg.py": LAB_RPC_DISCOVERY,
    "find_req_fields.py": LAB_RPC_DISCOVERY,
    "find_req_schema.py": LAB_RPC_DISCOVERY,
    "find_cn.py": LAB_RPC_DISCOVERY,
    "find_convert_vscode.py": LAB_RPC_DISCOVERY,
    "find_rpc_client.py": LAB_RPC_DISCOVERY,
    "search_schema_def.py": LAB_RPC_DISCOVERY,
    "search_code.py": LAB_RPC_DISCOVERY,

    # 4. Sondas de prueba RPC contra el daemon activo
    "test_daemons.py": LAB_RPC_TESTS,
    "read_hub61301.py": LAB_RPC_TESTS,
    "test_rpc_calls.py": LAB_RPC_TESTS,
    "test_rpc_markdown.py": LAB_RPC_TESTS,
    "inspect_cascade_trajectory.py": LAB_RPC_TESTS,
    "inspect_steps_detail.py": LAB_RPC_TESTS,
    "read_markdown_response.py": LAB_RPC_TESTS,
    "check_brain_steps.py": LAB_RPC_TESTS,
    "test_all_convs.py": LAB_RPC_TESTS,
    "test_extractor.py": LAB_RPC_TESTS,
}

print("Iniciando reorganizacion de archivos...")
moved_count = 0
for filename, target_dir in FILE_MAPPING.items():
    src_path = os.path.join(BASE_DIR, filename)
    dst_path = os.path.join(target_dir, filename)
    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)
        print(f"  [MOVED] {filename} -> {os.path.basename(target_dir)}/")
        moved_count += 1
    elif os.path.exists(dst_path):
        print(f"  [OK] Ya estaba en {os.path.basename(target_dir)}/: {filename}")
    else:
        print(f"  [SKIP] No existe: {filename}")

print(f"\nTotal archivos reubicados: {moved_count}")
