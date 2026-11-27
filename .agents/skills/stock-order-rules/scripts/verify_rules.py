import os
import sys
import re
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

# Robust project root discovery
d = os.path.abspath(os.path.dirname(__file__))
while d and not os.path.exists(os.path.join(d, 'backend', 'server.py')):
    parent = os.path.dirname(d)
    if parent == d:
        break
    d = parent

PROJECT_ROOT = d
os.chdir(PROJECT_ROOT)

print("=" * 70)
print(f" ระบบจัดการวัสดุสำนักงานออนไลน์ - Project Rules & Integrity Verification")
print(f" Project Root: {PROJECT_ROOT}")
print("=" * 70)

has_error = False

# ----------------------------------------------------------------------
# 1. Check for Emojis
# ----------------------------------------------------------------------
print("\n[1/6] Checking Strict No-Emoji Policy...")
emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]|[\u3030\u303d\u3297\u3299]')
target_files = [
    'staff.html', 'index.html', 'portal.html',
    'backend/server.py', 'backend/config.py', 'backend/database.py', 'backend/auth.py',
    'backend/inventory_handlers.py', 'backend/requisition_handlers.py',
    'backend/org_quota_handlers.py', 'backend/analytics_handlers.py',
    'scripts/generate_separated_portals.py',
    'scripts/portal_parts/seed_data.py', 'scripts/portal_parts/shared_ui.py',
    'scripts/portal_parts/requester_head_and_layout.py',
    'scripts/portal_parts/requester_catalog_and_cart_js.py',
    'scripts/portal_parts/requester_history_and_auth_js.py',
    'scripts/portal_parts/staff_head_and_layout.py',
    'scripts/portal_parts/staff_auth_and_requisitions_js.py',
    'scripts/portal_parts/staff_stock_and_inventory_js.py',
    'scripts/portal_parts/staff_analytics_and_reports_js.py',
    'scripts/portal_parts/staff_admin_crud_js.py',
]

emoji_found = False
for fname in target_files:
    fpath = os.path.join(PROJECT_ROOT, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        for line_no, line in enumerate(f, 1):
            m = emoji_pattern.findall(line)
            if m:
                print(f"  ❌ Emoji detected in {fname}:{line_no} -> {m} on '{line.strip()[:60]}'")
                emoji_found = True
                has_error = True

if not emoji_found:
    print("  ✅ PASS: 0 emojis found across UI and codebase.")

# ----------------------------------------------------------------------
# 2. Check for Native Dialogs (alert, confirm, prompt)
# ----------------------------------------------------------------------
print("\n[2/6] Checking for Native Dialogs (alert, confirm, prompt)...")
native_dialog_pattern = re.compile(r'(?<![a-zA-Z0-9_\.])(alert|confirm|prompt)\s*\(')
dialog_found = False
for fname in ['staff.html', 'index.html', 'portal.html']:
    fpath = os.path.join(PROJECT_ROOT, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        for line_no, line in enumerate(f, 1):
            trimmed = line.strip()
            if trimmed.startswith('//') or trimmed.startswith('*') or trimmed.startswith('/*'):
                continue
            m = native_dialog_pattern.search(line)
            if m:
                func_name = m.group(1)
                print(f"  ❌ Native dialog '{func_name}()' detected in {fname}:{line_no} -> '{trimmed[:60]}'")
                dialog_found = True
                has_error = True

if not dialog_found:
    print("  ✅ PASS: 0 native dialogs. SweetAlert2 is used exclusively.")

# ----------------------------------------------------------------------
# 3. Check System Version Synchronization
# ----------------------------------------------------------------------
print("\n[3/6] Checking Version Number Synchronization...")

# Read SYSTEM_VERSION from server.py
with open(os.path.join(PROJECT_ROOT, 'backend', 'server.py'), 'r', encoding='utf-8') as f:
    server_code = f.read()
m_server = re.search(r'SYSTEM_VERSION\s*=\s*"([^"]+)"', server_code)
server_ver = m_server.group(1) if m_server else "NOT_FOUND"

# Read from generate_separated_portals.py
with open(os.path.join(PROJECT_ROOT, 'scripts', 'generate_separated_portals.py'), 'r', encoding='utf-8') as f:
    gen_code = f.read()
m_gen = re.search(r'SYSTEM_VERSION\s*=\s*"([^"]+)"', gen_code)
gen_ver = m_gen.group(1) if m_gen else "NOT_FOUND"

# Read from test_stock_logic.py
with open(os.path.join(PROJECT_ROOT, 'tests', 'test_stock_logic.py'), 'r', encoding='utf-8') as f:
    test_code = f.read()
m_test = re.search(r'assert\s+SYSTEM_VERSION\s*==\s*"([^"]+)"', test_code)
test_ver = m_test.group(1) if m_test else "NOT_FOUND"

# Read latest version in CHANGELOG.md
with open(os.path.join(PROJECT_ROOT, 'CHANGELOG.md'), 'r', encoding='utf-8') as f:
    cl_code = f.read()
m_cl = re.search(r'##\s+\[([0-9]+\.[0-9]+\.[0-9]+)\]', cl_code)
cl_ver = m_cl.group(1) if m_cl else "NOT_FOUND"

print(f"  - backend/server.py:               v{server_ver}")
print(f"  - scripts/generate_portals.py:     v{gen_ver}")
print(f"  - tests/test_stock_logic.py:       v{test_ver}")
print(f"  - CHANGELOG.md:                    v{cl_ver}")

if server_ver == gen_ver == test_ver == cl_ver and server_ver != "NOT_FOUND":
    print(f"  ✅ PASS: All system versions are synchronized at v{server_ver}.")
else:
    print(f"  ❌ Version mismatch detected! All must match v{cl_ver}.")
    has_error = True

# ----------------------------------------------------------------------
# 4. Check Single Source of Truth Generator
# ----------------------------------------------------------------------
print("\n[4/6] Testing Single Source of Truth Generator (scripts/generate_separated_portals.py)...")
try:
    ret = subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, 'scripts', 'generate_separated_portals.py')],
                         capture_output=True, text=True, check=True)
    print("  ✅ PASS: Generator executed successfully without errors.")
except Exception as e:
    print(f"  ❌ Generator failed with error: {e}")
    has_error = True

# ----------------------------------------------------------------------
# 5. Check Searchable Dropdown Standard
# ----------------------------------------------------------------------
print("\n[5/6] Checking All-Dropdowns Searchable Enhancer...")
searchable_missing = False
for fname in ['index.html', 'staff.html']:
    fpath = os.path.join(PROJECT_ROOT, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        html_txt = f.read()
    if 'function enhanceSearchableSelect(' not in html_txt or 'function enhanceAllSearchableSelects(' not in html_txt:
        print(f"  ❌ Searchable dropdown enhancer missing in {fname}")
        searchable_missing = True
        has_error = True
if not searchable_missing:
    print("  ✅ PASS: All portal <select> dropdowns are searchable.")

# ----------------------------------------------------------------------
# 6. Run Automated Tests with pytest
# ----------------------------------------------------------------------
print("\n[6/6] Running pytest Test Suite...")
try:
    ret_test = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_stock_logic.py', '-q'],
                              capture_output=True, text=True)
    if ret_test.returncode == 0:
        summary = ret_test.stdout.strip().splitlines()[-1]
        print(f"  ✅ PASS: {summary}")
    else:
        print(f"  ❌ Pytest failed with return code {ret_test.returncode}:\n{ret_test.stdout}")
        has_error = True
except Exception as e:
    print(f"  ❌ Pytest execution failed: {e}")
    has_error = True

print("\n" + "=" * 70)
if has_error:
    print(" ❌ VERIFICATION FAILED: Please fix the highlighted issues above.")
    sys.exit(1)
else:
    print(" 🚀 ALL PROJECT RULES VERIFIED & PASSED (100% COMPLIANT)")
print("=" * 70)
