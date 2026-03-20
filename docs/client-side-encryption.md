# Client-Side Encryption

Client-Side Encryption with Per-User Keys and Django ORM Integration

---

## 1. Executive Summary

This architecture implements **Application-Layer Encryption** (often called **Client-Side Encryption** relative to the database) using a **Per-User Key** strategy.

Instead of relying on a single global key (which is a single point of failure), every user in the system is assigned a unique **Data Encryption Key (DEK)**. This key wraps their specific data. These DEKs are themselves encrypted by a master **Key Encryption Key (KEK)** managed by **Google Cloud KMS**.

**Security Guarantee:** The database (PostgreSQL) never sees plaintext data or the plaintext keys required to decrypt it. A database leak results in zero data compromise without also compromising the running application server and Google Cloud credentials.

This document outlines an approach that seamlessly integrates this encryption strategy into the **Django ORM**, making the encryption and decryption of data transparent to the developer.

---

## 2. Architecture Overview

### The "Two-Key" Envelope System

We utilize a hierarchy of keys to balance security and performance.

1. **KEK (Key Encryption Key):**
    * **Location:** Google Cloud KMS (Hardware Security Module).
    * **Role:** The "Master Lock." It never leaves Google. It is used only to encrypt/decrypt the User Keys (DEKs).
2. **DEK (Data Encryption Key):**
    * **Location:** Encrypted in the database (e.g., in the `users` table); Decrypted only in Application Memory (RAM).
    * **Role:** The "Worker Bee." Unique to every user. Used to encrypt/decrypt the actual database fields (e.g., SSNs, names).

---

## 3. Encryption/Decryption Utilities

At the core of this system are a few utility functions that interact with Google Cloud KMS and the `tink` cryptography library. In addition, to avoid a dependency on Google Cloud KMS during local development and in CI/CD pipelines, we use fake (mock) implementations of the KMS client and its AEAD primitive.

**[codeforlife/encryption.py](../codeforlife/encryption.py)**

---

## 4. Django ORM Integration

To make working with encrypted data seamless, we've integrated the encryption logic directly into Django's ORM. This is achieved through a combination of a base model class, custom model fields, and descriptors.

### Associated Data for Integrity

A core principle of this architecture is the use of **Associated Data** to ensure the integrity of encrypted values. Authenticated Encryption with Associated Data (AEAD) algorithms, like the AES-GCM we use, bind a piece of ciphertext to a specific context. This means that ciphertext encrypted in one context cannot be decrypted in another, which prevents certain attacks like swapping encrypted values between different database columns or rows.

To achieve this, we enforce the use of an `associated_data` string at two levels:

1. **Model-level:** Every `EncryptedModel` subclass must define a unique `associated_data` string. This scopes all encrypted fields within that model.
2. **Field-level:** Every `BaseEncryptedField` instance must be initialized with its own `associated_data` string, which must be unique within that model.

These two strings are combined to create a fully qualified identifier that is passed to the encryption and decryption functions. This provides two critical layers of integrity:

1. **Field-Level Integrity:** Consider a `Balance` model with two encrypted fields, `debit` and `credit`. The field-level AD ensures their values cannot be swapped. The AD for each would be `"balance:debit"` and `"balance:credit"`. An encrypted debit value cannot be moved to the credit column, as the decryption would fail due to the AD mismatch.

2. **Model-Level Integrity:** Now consider two different models, `Debit` and `Credit`, each with an encrypted `balance` field. The model-level AD prevents swapping values between them. The AD would be `"debit:balance"` and `"credit:balance"`. An encrypted balance from a `Debit` instance cannot be moved to a `Credit` instance, again because the AD would not match during decryption.

### Implementation

The implementation details can be found in the docstring of these files. It's recommended you read them in the following order.

1. **[codeforlife/models/encrypted.py](../codeforlife/models/encrypted.py):** This is the base class for any model that will contain encrypted fields.
1. **[codeforlife/models/fields/base_encrypted.py](../codeforlife/models/fields/base_encrypted.py):** This is where the core logic of transparent encryption and decryption happens.
1. **[codeforlife/models/fields/encrypted_text.py](../codeforlife/models/fields/encrypted_text.py):** A concrete encrypted text field which subclasses `BaseEncryptedField`.
1. **[codeforlife/models/base_data_encryption_key.py](../codeforlife/models/base_data_encryption_key.py):** This abstract model brings the `EncryptedModel` and `DataEncryptionKeyField` together.
1. **[codeforlife/models/data_encryption_key.py](../codeforlife/models/data_encryption_key.py):** This model inherits from `BaseDataEncryptionKeyModel` and conveniently includes the `dek` field by default.
1. **[codeforlife/models/fields/data_encryption_key.py](../codeforlife/models/fields/data_encryption_key.py):** This field is responsible for managing the lifecycle of a DEK for a model instance.

---

## 5. Usage Patterns

Here are two common patterns for using the encryption framework.

### Pattern 1: Self-Contained Encrypted Model

This is the simplest pattern. The model inherits from `DataEncryptionKeyModel`, which means it manages its own DEK and can have one or more encrypted fields. This is ideal for models that represent a primary entity, like a `User`.

```python
class User(DataEncryptionKeyModel):
    """
    A user model with an encrypted email. Because it inherits from
    DataEncryptionKeyModel, it automatically gets a 'dek' field to manage
    its own encryption key.
    """
    associated_data = "user" # Required for EncryptedModel

    username = models.CharField(max_length=150, unique=True)
    email = EncryptedTextField(associated_data="email")

    class Meta:
        app_label = "auth"

# --- Usage ---

# Create a new user. A new DEK is automatically generated and stored in the
# 'dek' field. The 'email' field is encrypted using this key.
user = User.objects.create(
    username="johndoe",
    email="john.doe@example.com"
)

# The 'dek' and 'email' fields are stored as encrypted bytes in the database.
# But when we access the 'email' attribute, it's decrypted automatically.
print(f"User's email: {user.email}")
# >>> User's email: john.doe@example.com

# You can update the email as you would with a normal field.
user.email = "john.doe.new@example.com"
user.save()
```

### Pattern 2: Delegated Encryption Key

Sometimes, you have a model whose data should be encrypted under another object's key. For example, a `Secret` that belongs to a `User`. The `Secret` itself doesn't need its own DEK; it should be encrypted with the `User`'s DEK.

In this case, the model inherits directly from `EncryptedModel` and must implement the `dek_aead` property to point to the key provider (the `User` model in this case).

```python
class Secret(EncryptedModel):
    """
    A model that stores a secret value. It does not have its own DEK.
    Instead, it relies on the related User's DEK for encryption.
    """
    associated_data = "secret" # Required for EncryptedModel

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="secrets")
    secret_value = EncryptedTextField(associated_data="secret-value")

    class Meta:
        app_label = "app"

    @property
    def dek_aead(self) -> Aead:
        """
        This model delegates encryption to the associated user's DEK.
        The `dek_aead` property is implemented to return the user's AEAD primitive.
        """
        return self.user.dek_aead

# --- Usage ---

# Assume 'user' is the User instance created in the previous example.
secret = Secret.objects.create(
    user=user,
    secret_value="my-super-secret-password"
)

# The 'secret_value' is encrypted using the DEK from the 'user' object.
# When accessed, it's decrypted using the same key.
print(f"The secret is: {secret.secret_value}")
# >>> The secret is: my-super-secret-password
```

---

## 6. Sequence Diagrams

This section contains diagrams that explain what the Django ORM is doing.

### 1. DEK Generation and Initial Save

This diagram shows the process that occurs when a new `EncryptedModel` instance (e.g., a `User`) is created and saved for the first time. The `EncryptedModel.save()` method is overridden to lazily manage the creation of the user-specific DEK.

```mermaid
sequenceDiagram
    actor Developer
    participant User as User (EncryptedModel)
    participant EncryptedModel as EncryptedModel (Base Class)
    participant GcpKmsClient as Tink/KMS Client
    participant PostgreSQL

    Developer->>User: user = User(name="test")
    Developer->>User: user.save()
    User->>EncryptedModel: save()
    activate EncryptedModel

    Note over EncryptedModel, GcpKmsClient: If self.pk is None (new user)
    EncryptedModel->>GcpKmsClient: create_dek()
    activate GcpKmsClient
    GcpKmsClient-->>EncryptedModel: Returns new encrypted DEK
    deactivate GcpKmsClient

    EncryptedModel->>User: self.dek = encrypted_dek
    Note over User, PostgreSQL: The model's save() method is called via super()
    User->>PostgreSQL: INSERT INTO users (name, dek)
    PostgreSQL-->>User: Returns
    deactivate EncryptedModel
```

### 2. Data Encryption

This diagram illustrates what happens when a developer sets a value on an encrypted field. The `EncryptedAttribute` descriptor intercepts the assignment, wrapping the plaintext value in a `_PendingEncryption` object. The actual encryption happens later, just before the model is saved to the database.

```mermaid
sequenceDiagram
    actor Developer
    participant User as User (Model Instance)
    participant EncryptedAttribute as EncryptedAttribute (Descriptor)
    participant _PendingEncryption as _PendingEncryption (Wrapper)
    participant BaseEncryptedField as BaseEncryptedField
    participant GcpKmsClient as Tink/KMS Client
    participant PostgreSQL

    Developer->>User: user.ssn = "123-456-7890"
    User->>EncryptedAttribute: __set__(user, "123-456-7890")
    activate EncryptedAttribute
    EncryptedAttribute->>_PendingEncryption: Create(value="123-456-7890")
    _PendingEncryption-->>EncryptedAttribute: Returns _PendingEncryption instance
    Note left of EncryptedAttribute: Caches are cleared
    EncryptedAttribute->>User: instance.__dict__["ssn"] = _PendingEncryption(...)
    deactivate EncryptedAttribute

    Developer->>User: user.save()
    User->>BaseEncryptedField: pre_save(user, True)
    activate BaseEncryptedField
    Note right of BaseEncryptedField: Checks for _PendingEncryption
    BaseEncryptedField->>GcpKmsClient: Decrypt user's DEK
    GcpKmsClient-->>BaseEncryptedField: Returns plaintext DEK
    BaseEncryptedField->>GcpKmsClient: encrypt(value, associated_data)
    GcpKmsClient-->>BaseEncryptedField: Returns ciphertext
    BaseEncryptedField-->>User: Returns ciphertext
    deactivate BaseEncryptedField
    User->>PostgreSQL: UPDATE users SET ssn=ciphertext
    PostgreSQL-->>User: Returns
```

### 3. Data Decryption

This diagram shows the process of reading an encrypted value from a model instance. The `EncryptedAttribute` descriptor checks an in-memory cache for the decrypted value first. If it's not cached, it decrypts the ciphertext from the database and populates the cache.

```mermaid
sequenceDiagram
    actor Developer
    participant User as User (Model Instance)
    participant EncryptedAttribute as EncryptedAttribute (Descriptor)
    participant GcpKmsClient as Tink/KMS Client

    Developer->>User: print(user.ssn)
    User->>EncryptedAttribute: __get__(user)
    activate EncryptedAttribute

    Note over User, EncryptedAttribute: Check instance.__decrypted_values__ cache
    alt Value is cached
        EncryptedAttribute-->>Developer: return instance.__decrypted_values__[field_name]
    else Value is not cached
        EncryptedAttribute->>User: Get ciphertext from instance.__dict__
        User-->>EncryptedAttribute: Returns ciphertext
        EncryptedAttribute->>GcpKmsClient: Decrypt user's DEK
        GcpKmsClient-->>EncryptedAttribute: Returns plaintext DEK
        EncryptedAttribute->>GcpKmsClient: decrypt(ciphertext, associated_data)
        GcpKmsClient-->>EncryptedAttribute: Returns plaintext value
        EncryptedAttribute->>User: instance.__decrypted_values__[field_name] = plaintext_value
        EncryptedAttribute-->>Developer: return plaintext_value
    end
    deactivate EncryptedAttribute
```

### 4. Data Shredding

Data shredding is achieved by nullifying the user's encrypted DEK. Once the key is gone, the data associated with it is rendered permanently unrecoverable.

```mermaid
sequenceDiagram
    actor Developer
    participant User as User (Model Instance)
    participant PostgreSQL

    Developer->>User: user.encrypted_dek = None
    Developer->>User: user.save()
    User->>PostgreSQL: UPDATE users SET encrypted_dek=NULL WHERE id=...
    PostgreSQL-->>User: Returns

    Note over Developer, PostgreSQL: The user's data (e.g., SSN) is now permanently unrecoverable.
```

### 5. Encrypted Model and Field Initialization

This diagram shows how an encrypted model and its fields are initialized and validated when Django starts up.

```mermaid
sequenceDiagram
    participant Django as Django Startup
    participant EncryptedModel as EncryptedModel (Class)
    participant BaseEncryptedField as BaseEncryptedField

    Django->>EncryptedModel: check()
    activate EncryptedModel
    
    Note over EncryptedModel: 1. Validate `associated_data`
    alt `associated_data` is not defined, not a string, or empty
        EncryptedModel-->>Django: raise Error
    end

    Note over EncryptedModel: 2. Check `associated_data` uniqueness
    alt `associated_data` is used by another model
        EncryptedModel-->>Django: raise Error
    end

    Note over EncryptedModel: 3. Validate Manager
    alt `objects` is not a subclass of `EncryptedModel.Manager`
        EncryptedModel-->>Django: raise Error
    end
    deactivate EncryptedModel

    Django->>BaseEncryptedField: contribute_to_class(EncryptedModel, "ssn")
    activate BaseEncryptedField
    
    Note over BaseEncryptedField: 4. Validate Model Subclass
    alt issubclass(Model, EncryptedModel) is False
        BaseEncryptedField-->>Django: raise ValidationError
    end

    Note over BaseEncryptedField: 5. Check for Duplicate Fields
    alt "ssn" is already in Model.ENCRYPTED_FIELDS
        BaseEncryptedField-->>Django: raise ValidationError
    end

    Note over BaseEncryptedField: 6. Check for Duplicate Associated Data
    alt "model:ssn" is already used by another field
        BaseEncryptedField-->>Django: raise ValidationError
    end

    Note over BaseEncryptedField: 7. Register Field
    BaseEncryptedField->>EncryptedModel: Model.ENCRYPTED_FIELDS.append(self)
    
    deactivate BaseEncryptedField
```

### 6. DEK Model and Field Initialization

This diagram details the validation that occurs when a `DataEncryptionKeyField` is added to a model. The field's `contribute_to_class` method ensures that the model is a valid `BaseDataEncryptionKeyModel` and that it contains only one DEK field.

```mermaid
sequenceDiagram
    participant Django as Django Startup
    participant DataEncryptionKeyField as DataEncryptionKeyField
    participant BaseDataEncryptionKeyModel as BaseDataEncryptionKeyModel (Class)

    Django->>DataEncryptionKeyField: contribute_to_class(Model, "dek")
    activate DataEncryptionKeyField

    Note over DataEncryptionKeyField: 1. Validate Model Subclass
    alt issubclass(Model, BaseDataEncryptionKeyModel) is False
        DataEncryptionKeyField-->>Django: raise ValidationError
    end

    Note over DataEncryptionKeyField: 2. Check for multiple DEK fields
    alt Model.DEK_FIELD is not None
        DataEncryptionKeyField-->>Django: raise ValidationError
    end

    Note over DataEncryptionKeyField: 3. Register Field on Model
    DataEncryptionKeyField->>BaseDataEncryptionKeyModel: Model.DEK_FIELD = self
    
    deactivate DataEncryptionKeyField
```

### 7. DEK AEAD Caching

To minimize latency and cost associated with decrypting the Data Encryption Key (DEK) via GCP KMS, the system employs an in-memory, time-to-live (TTL) cache for the AEAD primitive (`DEK_AEAD_CACHE`).

The following diagrams illustrate the two main caching flows: retrieval (cache hit/miss) and invalidation.

#### 7.1. Cache Retrieval (Hit & Miss)

This diagram shows how the `dek_aead` property on a `BaseDataEncryptionKeyModel` instance leverages the cache. A cache hit returns the stored AEAD primitive immediately, while a cache miss triggers a call to GCP KMS to decrypt the key, which is then cached for subsequent requests.

```mermaid
sequenceDiagram
    participant User
    participant EncryptedField as EncryptedField (__get__)
    participant DEKEnabledModel as DEK-Enabled Model
    participant DEK_AEAD_CACHE as TTLCache (in-memory)
    participant KMS as Google Cloud KMS

    User->>+EncryptedField: Accesses encrypted attribute
    EncryptedField->>+DEKEnabledModel: Accesses `dek_aead` property
    alt Cache Miss
        DEKEnabledModel->>DEK_AEAD_CACHE: Check for cached AEAD primitive (not found)
        DEKEnabledModel->>+KMS: Decrypt DEK using KEK
        KMS-->>-DEKEnabledModel: Returns AEAD primitive
        DEKEnabledModel->>DEK_AEAD_CACHE: Store AEAD primitive with instance PK
    else Cache Hit
        DEKEnabledModel->>DEK_AEAD_CACHE: Check for cached AEAD primitive (found)
        DEK_AEAD_CACHE-->>DEKEnabledModel: Return AEAD primitive
    end
    DEKEnabledModel-->>-EncryptedField: Return AEAD primitive
    EncryptedField->>EncryptedField: Decrypts data using AEAD primitive
    EncryptedField-->>-User: Returns decrypted value
```

#### 7.2. Cache Invalidation

The cache must be invalidated whenever the underlying DEK changes to prevent the use of stale keys. This happens automatically when the `DataEncryptionKeyField` is set, for example, during a data shredding operation where the key is set to `None`.

```mermaid
sequenceDiagram
    participant User
    participant DEKEnabledModel as DEK-Enabled Model
    participant DataEncryptionKeyAttribute as DataEncryptionKeyAttribute (__set__)
    participant DEK_AEAD_CACHE as TTLCache (in-memory)

    User->>+DEKEnabledModel: Shred data (e.g., `instance.dek = None`)
    DEKEnabledModel->>+DataEncryptionKeyAttribute: Sets `dek` field to new value
    DataEncryptionKeyAttribute->>+DEK_AEAD_CACHE: Delete cached AEAD for instance PK
    DEK_AEAD_CACHE-->>-DataEncryptionKeyAttribute: 
    DataEncryptionKeyAttribute->>DEKEnabledModel: Update `dek` value in `__dict__`
    DEKEnabledModel-->>-User: 
```
