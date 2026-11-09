import os
import glob

STEPS_DIR = r"C:\Users\cochr\.gemini\antigravity\brain\1cfae999-9108-4b5e-955e-667dd3eeee89\.system_generated\steps"
steps = os.listdir(STEPS_DIR)
print(f"Total steps in .system_generated/steps: {len(steps)}")
print(f"Sample step folders: {steps[:20]}")

for s in steps[:5]:
    step_path = os.path.join(STEPS_DIR, s)
    files = os.listdir(step_path)
    print(f"Step {s} files: {files}")
    for fl in files:
        if fl.endswith(".md") or fl.endswith(".txt"):
            with open(os.path.join(step_path, fl), "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
            print(f"   {fl} (len {len(c)}): {repr(c[:100])}")

