import os
from pathlib import PurePosixPath

import s3fs


def provide_s3_zarr_store():
    """Example provider, used to override providers from physrisk Container.

    Returns:
        MutableMapping: Zarr store.
    """
    access_key = os.environ.get("OSC_S3_ACCESS_KEY")
    secret_key = os.environ.get("OSC_S3_SECRET_KEY")
    s3_bucket = os.environ.get("OSC_S3_BUCKET")

    zarr_path = "hazard/hazard.zarr"

    s3 = s3fs.S3FileSystem(anon=False, key=access_key, secret=secret_key)

    store = s3fs.S3Map(
        root=str(PurePosixPath(s3_bucket, zarr_path)),
        s3=s3,
        check=False,
    )
    return store
