"""Quick PII detector performance test."""
import tempfile, time, sys, shutil
from pathlib import Path
sys.path.insert(0, 'src')

td = tempfile.mkdtemp()
project = Path(td) / 'test'
project.mkdir()

for i in range(50):
    f = project / f'svc_{i}.py'
    content = f'import asyncio\nclass S{i}:\n    pass\nemail = "u{i}__at__ex.com"\nphone = "555-123-4567"\n'
    f.write_text(content)

from code_migration.core.compliance.pii_detector import PIIDetector

t = time.time()
d = PIIDetector(project)
print(f'Init: {time.time()-t:.2f}s')

t = time.time()
r = d.scan_directory(file_extensions=['.py'])
print(f'Scan: {time.time()-t:.2f}s')
print(f'files={r["files_scanned"]}, findings={r["total_findings"]}')
d.close()
shutil.rmtree(td)
