import os
from pathlib import PurePosixPath
import pathlib

from dependency_injector import providers
from dotenv import load_dotenv
import s3fs
from physrisk.container import Container
from physrisk.hazard_models.hazard_cache import GeometryH3BasedCache, LMDBStore


def create_container():
    dotenv_dir = os.environ.get("CREDENTIAL_DOTENV_DIR", os.getcwd())
    dotenv_path = pathlib.Path(dotenv_dir) / "credentials.env"
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path, override=True)
    container = Container()
    container.config.zarr_max_workers.override(16)
    container.override_providers(zarr_store=providers.Singleton(provide_s3_zarr_store))

    hazard_cache_dir = os.environ.get("PHYSRISK_CACHE_DIR", "/tmp")
    # cache any API calls to LMDB, on a volume, location specified by env variable
    container.override_providers(
        cache_store=providers.Singleton(
            GeometryH3BasedCache,
            store=LMDBStore(str(pathlib.Path(hazard_cache_dir) / "hazard_cache.db")),
        )
    )

    return container


def provide_s3_zarr_store():
    """Example provider, used to override providers from physrisk Container.

    Returns:
        MutableMapping: Zarr store.
    """
    use_dev_bucket = False
    if use_dev_bucket:
        access_key = os.environ.get("OSC_S3_ACCESS_KEY_DEV", "")
        secret_key = os.environ.get("OSC_S3_SECRET_KEY_DEV", "")
        s3_bucket = os.environ.get("OSC_S3_BUCKET_DEV", "")
        zarr_path = os.environ.get("OSC_S3_HAZARD_PATH_DEV", "hazard/hazard.zarr")
    else:
        access_key = os.environ.get("OSC_S3_ACCESS_KEY", "")
        secret_key = os.environ.get("OSC_S3_SECRET_KEY", "")
        s3_bucket = os.environ.get("OSC_S3_BUCKET", "os-climate-physical-risk")
        zarr_path = os.environ.get(
            "OSC_S3_HAZARD_PATH", "hazard-indicators/hazard.zarr"
        )

    s3 = (
        s3fs.S3FileSystem(anon=True)
        if access_key == ""
        else s3fs.S3FileSystem(anon=False, key=access_key, secret=secret_key)
    )

    store = s3fs.S3Map(
        root=str(PurePosixPath(s3_bucket, zarr_path)),
        s3=s3,
        check=False,
    )
    return store
