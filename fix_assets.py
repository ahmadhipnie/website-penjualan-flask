import re

# Read the file
with open('templates/landing/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all img src paths
patterns = [
    (r'src="img/([^"]+)"', r'src="{{ url_for(\'static\', filename=\'assets_landing/img/\1\') }}"'),
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# Write back
with open('templates/landing/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Asset paths fixed successfully!")
