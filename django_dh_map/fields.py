from django.db import models
from django_ffield.fields import FileFField
from admin_async_upload.models import AsyncFileField

from .validators import FileTypeValidator, FixFileTypeValidator

class AsyncFFileField(FileFField, AsyncFileField):
    # use custom validator
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # remove FileFField's problematic validator (file needs to be reopened when async)
        self.validators = [validator for validator in self.validators if not isinstance(validator, FileTypeValidator)]
        if self.allowd_types or self.disallowed_types:
            self.validators.append(
                FixFileTypeValidator(allowd_types=self.allowd_types, disallowed_types=self.disallowed_types,)
            )
    pass

class AsyncImageFFileField(models.ImageField, AsyncFFileField):
    pass
