import os
import mimetypes
from django.shortcuts import get_object_or_404
from .file_manager_model import FileManager
from .storage_backends import get_storage_backend # 假设你的路径

def save_file_to_manager(file, user_id, parent=None, is_public=False):
    """
    通用文件保存逻辑，供 API 和内部业务调用
    """
    folder_path = parent.path if parent else ''
    storage = get_storage_backend()
    
    # 1. 计算文件信息
    file_ext = os.path.splitext(file.name)[1].lower()
    mime_type = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
    
    # 2. 保存到物理存储 (S3/本地/等)
    storage_path, url = storage.save(file, file.name, folder_path)
    
    # 3. 计算MD5
    md5 = storage.calculate_md5(file)
    
    # 4. 构建完整路径
    full_path = os.path.join(folder_path, file.name).replace('\\', '/')
    
    # 5. 创建数据库记录
    return FileManager.objects.create(
        name=file.name,
        type='file',
        parent=parent,
        path=full_path,
        size=file.size,
        file_ext=file_ext,
        mime_type=mime_type,
        storage_type=storage.__class__.__name__.replace('StorageBackend', '').lower(),
        storage_path=storage_path,
        url=url,
        md5=md5,
        is_public=is_public,
        sys_creator_id=user_id,
    )