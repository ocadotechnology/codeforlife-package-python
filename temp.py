import base64
import binascii
import json
from pathlib import Path
from typing import Any

import django


def setup_django():
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()


def generate_dek_value() -> str:
    from codeforlife.encryption import create_dek

    return base64.b64encode(create_dek()).decode("utf-8")


def build_fake_aead_from_fixture_dek(dek_value: str):
    from codeforlife.encryption import FakeAead, _get_kek_aead

    dek_bytes = base64.b64decode(dek_value)
    raw_dek = _get_kek_aead().decrypt(dek_bytes, b"")

    return FakeAead(raw_dek)


def update_encrypted_fields(fields: dict) -> int:
    dek_value = fields.get("dek")
    if not dek_value:
        return 0

    fake_aead = build_fake_aead_from_fixture_dek(dek_value)
    updated_count = 0

    for key, value in fields.items():
        if not key.endswith("_enc"):
            continue

        prefix = key.removesuffix("_enc")
        plain_key = f"{prefix}_plain"
        plain_value = fields.get(plain_key)
        if plain_value is None:
            continue

        plain_bytes = str(plain_value).encode("utf-8")
        associated_data = prefix.encode("utf-8")

        should_update = True
        if isinstance(value, str) and value:
            try:
                existing_ciphertext = base64.b64decode(value)
                decrypted_value = fake_aead.decrypt(
                    existing_ciphertext,
                    associated_data,
                )
                should_update = decrypted_value != plain_bytes
            except (ValueError, TypeError, binascii.Error):
                should_update = True

        if should_update:
            encrypted_value = fake_aead.encrypt(plain_bytes, associated_data)
            fields[key] = base64.b64encode(encrypted_value).decode("utf-8")
            updated_count += 1

    return updated_count


def update_hashed_fields(fields: dict) -> int:
    updated_count = 0

    for key, value in fields.items():
        if not key.endswith("_hash"):
            continue

        prefix = key.removesuffix("_hash")
        plain_key = f"{prefix}_plain"
        plain_value = fields.get(plain_key)
        if plain_value is None:
            continue

        new_value = str(plain_value)
        if value != new_value:
            fields[key] = new_value
            updated_count += 1

    return updated_count


def sort_model_fields(object_data: dict) -> int:
    fields = object_data.get("fields")
    if not isinstance(fields, dict):
        return 0

    sorted_keys = sorted(fields)
    if list(fields) == sorted_keys:
        return 0

    object_data["fields"] = {key: fields[key] for key in sorted_keys}
    return 1


def load_reference_fixture(
    reference_fixture_path: Path,
) -> dict[tuple[str, int], dict[str, Any]]:
    if not reference_fixture_path.exists():
        return {}

    with reference_fixture_path.open("r", encoding="utf-8") as fixture_file:
        fixture_data = json.load(fixture_file)

    lookup: dict[tuple[str, int], dict[str, Any]] = {}
    for object_data in fixture_data:
        model = object_data.get("model")
        pk = object_data.get("pk")
        fields = object_data.get("fields")

        if not isinstance(model, str) or not isinstance(pk, int):
            continue
        if not isinstance(fields, dict):
            continue

        lookup[(model, pk)] = fields

    return lookup


def update_username_fields(
    object_data: dict,
    fields: dict,
    reference_lookup: dict[tuple[str, int], dict[str, Any]],
) -> int:
    if object_data.get("model") != "user.user":
        return 0

    pk = object_data.get("pk")
    if not isinstance(pk, int):
        return 0

    reference_fields = reference_lookup.get(("user.user", pk))
    if not reference_fields:
        return 0

    username = reference_fields.get("username")
    if not isinstance(username, str):
        return 0

    updated_count = 0

    if fields.get("username_plain") != username:
        fields["username_plain"] = username
        updated_count += 1

    if "username_enc" not in fields:
        fields["username_enc"] = ""
        updated_count += 1

    if "username_hash" not in fields:
        fields["username_hash"] = ""
        updated_count += 1

    return updated_count


def update_fixture_file(
    fixture_path: Path, reference_fixture_path: Path
) -> int:
    with fixture_path.open("r", encoding="utf-8") as fixture_file:
        fixture_data = json.load(fixture_file)

    reference_lookup = load_reference_fixture(reference_fixture_path)

    updated_count = 0
    for object_data in fixture_data:
        if object_data.get("model") not in {"user.user", "user.school"}:
            updated_count += sort_model_fields(object_data)
            continue

        fields = object_data.setdefault("fields", {})
        updated_count += update_username_fields(
            object_data,
            fields,
            reference_lookup,
        )

        if "dek" not in fields:
            fields["dek"] = generate_dek_value()
            updated_count += 1

        updated_count += update_encrypted_fields(fields)
        updated_count += update_hashed_fields(fields)
        updated_count += sort_model_fields(object_data)

    if updated_count:
        with fixture_path.open("w", encoding="utf-8") as fixture_file:
            json.dump(fixture_data, fixture_file, indent=2)
            fixture_file.write("\n")

    return updated_count


def main():
    setup_django()

    fixtures_dir = (
        Path(__file__).resolve().parent / "codeforlife" / "user" / "fixtures"
    )
    reference_dir = Path(__file__).resolve().parent / "temp"
    total_updated = 0

    for fixture_path in sorted(fixtures_dir.glob("*.json")):
        reference_fixture_path = reference_dir / fixture_path.name
        updated_in_file = update_fixture_file(
            fixture_path,
            reference_fixture_path,
        )
        if updated_in_file:
            print(f"Updated {updated_in_file} objects in {fixture_path.name}")
            total_updated += updated_in_file

    print(f"Done. Updated {total_updated} total objects.")


if __name__ == "__main__":
    main()
