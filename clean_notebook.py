import json

notebook_path = 'notebooks/tinyllama_finetuning.ipynb'

# قراءة الملف
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# حذف widgets من metadata الرئيسي
if 'widgets' in nb.get('metadata', {}):
    del nb['metadata']['widgets']
    print("Removed top-level widgets metadata")

# حذف widgets من metadata كل خلية
for i, cell in enumerate(nb.get('cells', [])):
    if 'widgets' in cell.get('metadata', {}):
        del cell['metadata']['widgets']
        print(f"Removed widgets from cell {i}")

# حفظ الملف النظيف
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("✅ تم تنظيف النوت بوك بالكامل")
