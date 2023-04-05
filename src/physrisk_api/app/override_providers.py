import os
from pathlib import PurePosixPath

import s3fs
from physrisk.data.inventory_reader import InventoryReader

s3_bucket = "redhat-osc-physical-landing-647521352890"
zarr_path = "hazard/hazard.zarr"


def create_s3fs_instance():
    access_key = os.environ.get("OSC_S3_ACCESS_KEY")
    secret_key = os.environ.get("OSC_S3_SECRET_KEY")
    s3 = s3fs.S3FileSystem(anon=False, key=access_key, secret=secret_key)
    return s3


def provide_inventory_reader():
    return InventoryReader(fs=create_s3fs_instance(), base_path=s3_bucket)


def provide_s3_zarr_store():
    s3 = create_s3fs_instance()
    store = s3fs.S3Map(
        root=str(PurePosixPath(s3_bucket, zarr_path)),
        s3=s3,
        check=False,
    )
    return store
