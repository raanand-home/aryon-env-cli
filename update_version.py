import subprocess
import re
with open('pyproject.toml') as f:
    original = f.read()
describe = subprocess.check_output(["git","describe"]).decode('utf-8')
splited_describe = describe.split('-')
new_version = f"{splited_describe[0].replace('v','')}.{splited_describe[1]}"
def onmatch(f):
    raise Exception(f)
content = re.sub(
    r"\nversion.*",
    f"\nversion = \"{new_version}\"",
    original,
)

with open('pyproject.toml','w') as f:
    f.write(content)