import os
import shutil

# Create implementation folder
os.makedirs("implementation", exist_ok=True)
print("✅ Created 'implementation' folder")

# List of MD files to move
files_to_move = [
    "HTTPS_IMPLEMENTATION.md",
    "HTTPS_MIGRATION.md", 
    "MIGRATION_GUIDE.md",
    "MIGRATION_SUMMARY.md",
    "QUICKSTART.md",
    "QUICK_MIGRATION_REFERENCE.md",
    "ROLES_GUIDE.md"
]

# Move files
for file in files_to_move:
    src = file
    dst = f"implementation/{file}"
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"✅ Moved {file} → implementation/{file}")
    else:
        print(f"⚠️  File not found: {file}")

print("\n✅ All implementation docs moved to 'implementation/' folder!")
print("\n📁 Contents of implementation folder:")
for item in os.listdir("implementation"):
    print(f"   - {item}")
