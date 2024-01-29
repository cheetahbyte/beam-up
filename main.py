import sys, lzma, tarfile, pyAesCrypt, datetime, tempfile, os
from minio import Minio

def compress(folder_name: str) -> None:

    xz = lzma.LZMAFile(f"{folder_name}.tar.xz", "w")
    with tarfile.open(fileobj=xz, mode="w") as tar:
        tar.add(folder_name)
    xz.close()

def encrypt(filename: str) -> None:
    pyAesCrypt.encryptFile(filename, filename + ".enc", os.getenv("PASSWORD"), 64 * 1024)

def decrypt(filename: str) -> None:
    pyAesCrypt.decryptFile(filename, filename[:-4] , os.getenv("PASSWORD") , 64 * 1024)

def upload(backedupFolder: str, filename: str) -> None:
    client = Minio(
        os.getenv("S3_ENDPOINT"),
        access_key=os.getenv("S3_ACCESS_KEY"),
        secret_key=os.getenv("S3_SECRET_KEY"),
        secure=True
    )
    bucket_name = backedupFolder + "-backup"
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)

    client.fput_object(bucket_name, f"backup-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}.tar.xz.enc", filename)

def main() -> None:
    folder: str = sys.argv[1]
    backupFile = tempfile.NamedTemporaryFile(prefix="beamup-")
    compress(folder)
    encrypt(backupFile.name)
    upload(folder, backupFile.name + ".enc")
    backupFile.close()
    

if __name__ == "__main__":
    folder: str = sys.argv[1]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    main()