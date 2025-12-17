import os
from datetime import datetime

EXPORT_DIR = "storage/exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_csv(df, prefix="analytics"):
    """
    Save current DataFrame to CSV with timestamped filename.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.csv"
    path = os.path.join(EXPORT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"[CSV Export] Saved to {path}")
    return path
