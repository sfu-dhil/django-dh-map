from django.core.exceptions import ValidationError
from django_ffield.utils import meme_type

from django_ffield.validators import FileTypeValidator

class FixFileTypeValidator(FileTypeValidator):
    def __call__(self, file) -> None:
        """called by django validator

        Parameters
        ----------
        file : FileIO
            the file input that passed by django to validate

        Raises
        ------
        ValidationError
            when the file don't match by selected types this error raises to show to user
        """
        file.open()
        typ, formt = meme_type(file)

        # * to prevent forbidden upload files by user
        if self.allowd_types  and  typ not in self.allowd_types and formt not in self.allowd_types:
            raise ValidationError(
                f"Unsupported Format: The {formt} type is not in allowd supported formats. Supported formats: {self.allowd_types}. Unsupported formats: {self.disallowed_types}. "
            )
        elif self.disallowed_types  and typ in self.disallowed_types or formt in self.disallowed_types :
            raise ValidationError(
                f"Unsupported Format: The {formt} type is not supported formats. Unsupported formats: {self.disallowed_types}."
            )
