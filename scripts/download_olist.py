"""Fetch original public Olist CSVs using kagglehub. Optional network action on user's machine."""
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'data/raw';DEST.mkdir(parents=True,exist_ok=True)
try:
    import kagglehub
except ImportError:
    sys.exit('Install first: pip install kagglehub')
print('Downloading public Olist Kaggle dataset (network required)...')
source=Path(kagglehub.dataset_download('olistbr/brazilian-ecommerce'))
filenames=['olist_orders_dataset.csv','olist_customers_dataset.csv','olist_order_items_dataset.csv','olist_order_payments_dataset.csv',
           'olist_order_reviews_dataset.csv','olist_products_dataset.csv','product_category_name_translation.csv']
missing=[x for x in filenames if not (source/x).exists()]
if missing:sys.exit(f'Download incomplete. Missing: {missing}; original local files not changed.')
for x in filenames:shutil.copy2(source/x,DEST/x)
(DEST/'SYNTHETIC_DEMO_DATA.txt').unlink(missing_ok=True)
print(f'Success: copied {len(filenames)} authentic CSVs into {DEST}. Now run: python scripts/quickstart.py')
