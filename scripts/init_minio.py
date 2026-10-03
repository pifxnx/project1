from src.core.storage import minio

BUCKETS = {
    "reports": "Сегенерированные отчеты",
    "exports": "Экспортированные данные",
    "imports": "Загруженные файлы для импорта"
}

def initialize_minio_buckets():
    for bucket_name in BUCKETS.keys():
        if not minio.client.bucket_exists(bucket_name):
            minio.client.make_bucket(bucket_name)
            print(f"Created bucket: {bucket_name}")


if __name__ == "__main__":
    initialize_minio_buckets()