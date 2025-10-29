import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
REAL_DIR = os.path.join(DATA_DIR, 'real')
SYNTHETIC_DIR = os.path.join(DATA_DIR, 'synthetic')

# Define which folders/files are real or synthetic (add more as needed)
REAL_FOLDERS = [
    'ptb-xl',
    'real',
    'real_public',
    'cardiology',
    'production',
]
SYNTHETIC_FOLDERS = [
    'synthetic',
]

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def move_to_subdir(item, subdir):
    src = os.path.join(DATA_DIR, item)
    dst = os.path.join(subdir, item)
    if os.path.exists(src):
        print(f"Moving {src} -> {dst}")
        if os.path.exists(dst):
            print(f"Target {dst} already exists. Removing source {src}.")
            if os.path.isdir(src):
                shutil.rmtree(src)
            else:
                os.remove(src)
        else:
            shutil.move(src, dst)

def clean_data_dir():
    # Move real folders/files
    ensure_dir(REAL_DIR)
    for item in os.listdir(DATA_DIR):
        if item in REAL_FOLDERS and item not in ['real', 'synthetic']:
            move_to_subdir(item, REAL_DIR)
    # Move synthetic folders/files
    ensure_dir(SYNTHETIC_DIR)
    for item in os.listdir(DATA_DIR):
        if item in SYNTHETIC_FOLDERS and item != 'synthetic':
            move_to_subdir(item, SYNTHETIC_DIR)
    # Delete everything else except 'real' and 'synthetic'
    for item in os.listdir(DATA_DIR):
        if item not in ['real', 'synthetic']:
            item_path = os.path.join(DATA_DIR, item)
            print(f"Deleting unrequired {item_path}")
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

def main():
    clean_data_dir()
    print("\nData directory is now organized into 'real' and 'synthetic' only. All other files/folders have been removed.")

if __name__ == "__main__":
    main()
import os
import shutil


# Map of dataset source (relative to data/production) to target (relative to data/)
DATASET_MAP = {
    # Cardiology
    'cardiology/ptb-xl': 'ptb-xl',
    # Dermatology
    'dermatology/ham10000': 'ham10000',
    # Gastroenterology
    'gastro/gastrointestinal_lesions': 'gastrointestinal_lesions',
    # General
    'general/mimic-iv': 'mimic-iv',
    # Orthopedics
    'orthopedics/mura': 'mura',
    # Respiratory
    'respiratory/chest_xray': 'chest_xray',
    # Router (if any shared dataset)
}

REQUIRED_FOLDERS = set(DATASET_MAP.values())

ROOT = os.path.dirname(os.path.abspath(__file__))
PROD_DATA = os.path.join(ROOT, 'data', 'production')
TARGET_DATA = os.path.join(ROOT, 'data')


def copytree(src, dst):
    if os.path.exists(dst):
        print(f"Target {dst} already exists. Skipping copy.")
        return
    print(f"Copying {src} -> {dst}")
    shutil.copytree(src, dst)

def remove_unrequired_data():
    for item in os.listdir(TARGET_DATA):
        item_path = os.path.join(TARGET_DATA, item)
        if item == 'production':
            continue  # Don't delete the production folder
        if item not in REQUIRED_FOLDERS:
            print(f"Deleting unrequired {item_path}")
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)


def main():
    # Copy required datasets
    for src_rel, dst_rel in DATASET_MAP.items():
        src = os.path.join(PROD_DATA, src_rel)
        dst = os.path.join(TARGET_DATA, dst_rel)
        if not os.path.exists(src):
            print(f"Source {src} does not exist. Skipping.")
            continue
        copytree(src, dst)
    # Remove unrequired data
    remove_unrequired_data()
    print("\nAll required datasets are now in data/. Unrequired files/folders have been deleted.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
