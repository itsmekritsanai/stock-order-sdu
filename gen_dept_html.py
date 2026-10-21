import json

with open('departments_structured.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

html = []
for category, parents in data.items():
    html.append(f'  <optgroup label="{category}">')
    for parent, subs in parents.items():
        if subs:
            html.append(f'    <option value="{parent}">{parent} (ภาพรวม)</option>')
            for sub in subs:
                html.append(f'    <option value="{parent} ({sub})">&nbsp;&nbsp;↳ {sub} ({parent})</option>')
        else:
            html.append(f'    <option value="{parent}">{parent}</option>')
    html.append('  </optgroup>')

opt_str = '\n'.join(html)
with open('dept_options.html', 'w', encoding='utf-8') as out:
    out.write(opt_str)

print("Created dept_options.html with", len(html), "lines.")
