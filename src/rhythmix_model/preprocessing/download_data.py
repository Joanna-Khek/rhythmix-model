import pandas as pd
import kagglehub
import os
import shutil
from conf import settings
from pathlib import Path


def download_data(data_dir: Path, kaggle_data: str, kaggle_file: str) -> None:
    """
    Downloads the dataset from Kaggle and saves it to the specified directory.

    Args:
        data_dir (Path): The directory where the dataset will be saved.
        kaggle_data (str): The Kaggle dataset identifier.
        kaggle_file (str): The name of the file to be saved.
    """

    # Create new directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Download the latest version (version 1) dataset
    kagglehub.dataset_download(kaggle_data + "/versions/1")

    # Check if the downloaded file exists
    download_dir = Path(settings.ROOT, "datasets")
    default_kaggle_dir = Path(download_dir, kaggle_data)

    if not default_kaggle_dir.exists():
        raise FileNotFoundError(f"The directory {default_kaggle_dir} does not exist.")

    # Move the downloaded file to the specified directory
    shutil.move(
        Path(default_kaggle_dir, "versions/1", kaggle_file),
        Path(data_dir, kaggle_file),
    )

    # Remove the downloaded dataset folder
    shutil.rmtree(download_dir)


def clean_data(data_path: Path, save_path: Path) -> None:
    """Perform data cleaning on the raw dataset

    Args:
        df (pd.DataFrame): Raw dataset downloaded from Kaggle
    """
    # Read dataset
    df = pd.read_csv(data_path)

    # Clean dataset and add track link column
    df_clean = (
        df.assign(
            track_link=lambda df_: "https://open.spotify.com/track/" + df_["track_id"]
        )
        .drop_duplicates(subset=["artists", "track_name"], keep="first")
        .reset_index(drop=True)
        .drop("Unnamed: 0", axis=1)
    )
    df_clean.to_csv(save_path, index=False)


if __name__ == "__main__":
    os.environ["KAGGLEHUB_CACHE"] = str(settings.ROOT)

    # Download the dataset
    print("Downloading dataset...")
    download_data(
        data_dir=Path(settings.DATA_DIR),
        kaggle_data="thedevastator/spotify-tracks-genre-dataset",
        kaggle_file="train.csv",
    )

    # Perform data cleaning
    print("Cleaning dataset...")
    clean_data(
        data_path=Path(settings.DATA_DIR, "train.csv"),
        save_path=Path(settings.DATA_DIR, "clean_data.csv"),
    )
