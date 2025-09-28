import hashlib
from django.db import models


class HashDiffConfig:
    fields: list = []

    def __init__(self, fields: list[str] = None):
        self.fields = fields


class HashDiffMixin(models.Model):
    """
    Abstract Django mixin for computing and storing a hash of selected fields
    to enable idempotency checks (hash_diff).

    Usage:
        1. Inherit from this mixin in your SCD2 or versioned model.
        2. Define `hash_diff_fields` as a list of model field names to include
           in the hash computation.
        3. On save, the hash is automatically computed. If the hash is identical
           to the previous one, the save is skipped (prevents unnecessary updates).

    Example:
        class EntityDetail(HashDiffMixin, SCD2BaseModel):
            detail_code = models.CharField(max_length=100)
            value = models.TextField()
            hash_diff_fields = ['detail_code', 'value']
    """
    # Fields
    hash_diff = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="SHA-256 hash of the normalized business value for idempotency."
    )

    # Tech attributes (Not stored in DB)
    hash_diff_config: HashDiffConfig

    class Meta:
        abstract = True

    def compute_hash_diff(self) -> str:
        """
        Computes SHA-256 hash of the concatenated values of the fields specified
        in `hash_diff_fields`. Each value is converted to string and separated by '|'.
        Returns an empty string if `hash_diff_fields` is not defined.
        """
        if not self.hash_diff_config.fields:
            return ""

        normalized = "|".join(str(getattr(self, f, "")) for f in self.hash_diff_config.fields)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def save(self, *args, **kwargs):
        """
        Overrides the default save method:
        1. Computes the hash for the fields in `hash_diff_fields`.
        2. If the new hash matches the existing `hash_diff`, the save is skipped
           (idempotent behavior).
        3. Otherwise, updates `hash_diff` and calls the superclass save method.
        """
        if self.hash_diff_config.fields and self.pk:
            # kwargs["hash_diff_checked"] = True
            new_hash = self.compute_hash_diff()
            if new_hash == self.hash_diff:
                return
            self.hash_diff = new_hash

        super().save(*args, **kwargs)
