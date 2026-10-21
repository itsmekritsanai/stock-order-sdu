import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('คณะและหน่วยงาน.txt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
current_category = "คณะ / โรงเรียน"
current_parent = "ทั่วไป"

structured_data = {
    "คณะ / โรงเรียน": {},
    "สถาบัน / สำนัก / ศูนย์ / กอง": {}
}

for line in lines:
    line = line.strip()
    if 'สถาบัน/สำนัก/ศูนย์' in line:
        current_category = "สถาบัน / สำนัก / ศูนย์ / กอง"
        continue
    elif 'คณะ' in line and 'font-size: 18px' in line:
        current_category = "คณะ / โรงเรียน"
        continue

    # Main units in <p>
    p_links = re.findall(r'<p>(.*?)</p>', line)
    if p_links:
        for p in p_links:
            parts = re.split(r'<br\s*/?>', p)
            for part in parts:
                clean_name = re.sub(r'<[^>]+>', '', part).strip()
                if clean_name and not clean_name.startswith('&nbsp;'):
                    current_parent = clean_name
                    if current_parent not in structured_data[current_category]:
                        structured_data[current_category][current_parent] = []

    # Sub items in <li>
    li_items = re.findall(r'<li[^>]*>(.*?)</li>', line)
    if li_items:
        for li in li_items:
            clean_name = re.sub(r'<[^>]+>', '', li).strip()
            clean_name = re.sub(r'\s+', ' ', clean_name).strip()
            if clean_name:
                if current_parent not in structured_data[current_category]:
                    structured_data[current_category][current_parent] = []
                structured_data[current_category][current_parent].append(clean_name)

print("Parsed categories:")
flat_list = []
for cat, parents in structured_data.items():
    print(f"=== {cat} ({len(parents)} units) ===")
    for p, subs in parents.items():
        flat_list.append(p)
        for s in subs:
            flat_list.append(f"{p} - {s}")

print(f"Total options: {len(flat_list)}")
with open('departments_structured.json', 'w', encoding='utf-8') as f:
    json.dump(structured_data, f, ensure_ascii=False, indent=2)
