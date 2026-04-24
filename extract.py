import re, json

f = r'c:\Users\ShahinJahromi\AppData\Roaming\Code\User\workspaceStorage\a50a14fc5def68d1812387f57a1e28d4\GitHub.copilot-chat\transcripts\29a25ff6-b156-46b0-a94d-1dd340f07b4a.jsonl'
out = []
with open(f, 'r', encoding='utf-8') as file:
    for line in file:
        if 'replace_string_in_file' in line and 'generate_reqs.py' in line:
            try:
                data = json.loads(line)
                args = data['data']['arguments']
                new_str = args['newString']
                out.append(new_str)
            except: pass

with open('dumped_generate_reqs.py', 'w', encoding='utf-8') as file:
    file.write('\n'.join(out))
print("done")
