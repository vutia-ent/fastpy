# Storage Facade

File storage with multiple backend support.

## Supported Disks

- `local` (default) - Local filesystem
- `s3` - AWS S3
- `memory` - In-memory (testing)

## Basic Usage

```python
from fastpy_cli.libs import Storage

# Store file
Storage.put('avatars/user.jpg', file_content)

# Get file content
content = Storage.get('avatars/user.jpg')

# Check existence
if Storage.exists('avatars/user.jpg'):
    print('File exists')

if Storage.missing('avatars/user.jpg'):
    print('File does not exist')

# Delete file
Storage.delete('avatars/user.jpg')
```

## File URLs

```python
# Get public URL
url = Storage.url('avatars/user.jpg')

# For S3, returns signed URL or public URL
url = Storage.disk('s3').url('documents/report.pdf')
```

## File Information

```python
# Get file size (bytes)
size = Storage.size('documents/report.pdf')

# Get last modified time
modified = Storage.last_modified('documents/report.pdf')
```

## Uploading Files

```python
# Store uploaded file
from fastapi import UploadFile

@router.post("/upload")
async def upload(file: UploadFile):
    # Store with auto-generated name
    path = Storage.put_file('uploads', file)

    # Store with specific name
    path = Storage.put_file('uploads', file, name='custom-name.jpg')

    return {'path': path, 'url': Storage.url(path)}
```

## File Operations

```python
# Copy file
Storage.copy('source.jpg', 'destination.jpg')

# Move file
Storage.move('old-path.jpg', 'new-path.jpg')

# Append to file
Storage.append('logs/app.log', 'New log entry\n')

# Prepend to file
Storage.prepend('logs/app.log', 'First line\n')
```

## Directories

```python
# List files in directory
files = Storage.files('avatars/')

# List all files recursively
all_files = Storage.all_files('uploads/')

# List subdirectories
dirs = Storage.directories('uploads/')

# Create directory
Storage.make_directory('uploads/2024')

# Delete directory
Storage.delete_directory('uploads/temp')
```

## Using Specific Disk

```python
# Use S3
Storage.disk('s3').put('backups/db.sql', sql_dump)

# Use local disk
Storage.disk('local').put('temp/file.txt', content)

# Set default disk
Storage.set_default_disk('s3')
```

## Configuration

```bash
# Local storage
STORAGE_DISK=local
STORAGE_PATH=storage  # Relative to project root

# S3 storage
STORAGE_DISK=s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
AWS_BUCKET=my-bucket
AWS_URL=https://my-bucket.s3.amazonaws.com
```

## Custom Disks

```python
from fastpy_cli.libs.storage import StorageDriver

class CustomDriver(StorageDriver):
    def put(self, path: str, contents) -> bool:
        # Implementation
        pass

    def get(self, path: str) -> bytes:
        # Implementation
        pass

    def exists(self, path: str) -> bool:
        # Implementation
        pass

    def delete(self, path: str) -> bool:
        # Implementation
        pass

    def url(self, path: str) -> str:
        # Implementation
        pass

# Register custom disk
Storage.register_disk('custom', CustomDriver())
```

## Testing

```python
from fastpy_cli.libs import Storage

# Enable fake mode
Storage.fake()

# Use normally
Storage.put('test.txt', 'content')

# Assertions
Storage.assert_exists('test.txt')
Storage.assert_missing('other.txt')
```

## Complete Example

```python
from fastpy_cli.libs import Storage
from fastapi import UploadFile
import uuid

class FileService:
    def upload_avatar(self, user_id: int, file: UploadFile) -> str:
        # Generate unique filename
        ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = f"avatars/{user_id}/{filename}"

        # Store file
        Storage.put(path, file.file.read())

        # Return URL
        return Storage.url(path)

    def upload_document(self, file: UploadFile) -> dict:
        # Store to S3
        path = Storage.disk('s3').put_file('documents', file)

        return {
            'path': path,
            'url': Storage.disk('s3').url(path),
            'size': Storage.disk('s3').size(path)
        }

    def delete_user_files(self, user_id: int):
        # Delete all user files
        Storage.delete_directory(f'avatars/{user_id}')
        Storage.delete_directory(f'documents/{user_id}')

    def get_user_files(self, user_id: int) -> list:
        files = Storage.all_files(f'documents/{user_id}')
        return [
            {
                'path': f,
                'url': Storage.url(f),
                'size': Storage.size(f)
            }
            for f in files
        ]
```
