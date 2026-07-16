"""Reset vector store - use when mappings are corrupted"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import vector_store
import shutil


def reset_vector_store() -> None:
    """Reset vector store - use when mappings are corrupted"""
    print("Resetting vector store...")
    # Clear in-memory index
    vector_store.clear()
    
    # Remove files
    index_path = vector_store.index_path
    if index_path.exists():
        # Delete index file
        index_file = index_path / "faiss.index"
        if index_file.exists():
            index_file.unlink()
            print(f"Removed {index_file}")

        # Delete metadata file
        metadata_file = index_path / "metadata.json"
        if metadata_file.exists():
            metadata_file.unlink()
            print(f"Removed {metadata_file}")

    # Reinitialize vector store
    vector_store._load_index()

    print(" Vector store reset complete!")
    print(f"Total vectors: {vector_store.get_vector_count()}")
    print(f"Mappings: {len(vector_store.id_to_index)}")


if __name__ == "__main__":
    reset_vector_store()