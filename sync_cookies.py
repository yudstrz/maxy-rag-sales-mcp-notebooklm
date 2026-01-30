import json
from pathlib import Path

# Paths
user_home = Path.home()
auth_json_path = user_home / ".notebooklm-mcp" / "auth.json"
cookies_txt_path = Path("c:/Users/wahyu/Documents/GitHub/maxy-rag-sales-mcp-notebooklm/cookies.txt")

# Read auth.json
if not auth_json_path.exists():
    print(f"Error: {auth_json_path} not found")
    exit(1)

with open(auth_json_path, "r") as f:
    data = json.load(f)

cookies_dict = data.get("cookies", {})

# Construct cookie string
# Format: key=value; key=value
cookie_parts = []
for k, v in cookies_dict.items():
    cookie_parts.append(f"{k}={v}")

cookie_string = "; ".join(cookie_parts)

# Write to cookies.txt
with open(cookies_txt_path, "w") as f:
    f.write(cookie_string)

print(f"Successfully synced {len(cookies_dict)} cookies from auth.json to cookies.txt")
