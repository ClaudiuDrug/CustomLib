
# customlib

A few tools for day to day work.

---

### Installation:

```commandline
python -m pip install [--upgrade] customlib
```

---

### Available tools:

<details>
<summary>FileHandler</summary>
<p>

This is a file handler that can be used as a context-manager with thread & file locking.

How to:

```python
from customlib.filehandlers import FileHandler

with FileHandler("some_file.txt", "a", encoding="UTF-8") as fh:
    fh.write("Testing 'FileHandler'...")
```


</p>
</details>

---

<details>
<summary>FileLocker</summary>
<p>

This is a file locker that can also be used as a context-manager.

How to:

```python
from customlib.filelockers import FileLocker, LOCK

fl1 = FileLocker()

if __name__ == '__main__':
    fh1 = open("just_a_file.txt", "w", encoding="UTF-8")
    fl1.acquire(fh1, flags=LOCK.EX)
    fh1.write("Just testing the locking system...\n")
    fl1.release(fh1)
    fh1.close()
```

**Lock types:**
- `LOCK.EX`: int (0x1), exclusive lock
- `LOCK.SH`: int (0x2), shared lock

**Lock flags:**
- `LOCK.NB`: int (0x4), non-blocking

**Manually unlock (only needed internally):**
- `LOCK.UN`: int (0), unlock


</p>
</details>

---

<details>
<summary>Vault</summary>
<p>

This is a handler that makes use of keyring for password safe-keeping.

How to:

```python
from customlib.keyvault import Vault

vault = Vault()
password: str = vault.generate(exclude="\'\"\\", length=16)
vault.set_password(service="test_service", username="test_username", password=password)


if __name__ == '__main__':
    password: str = vault.get_password(service="test_service", username="test_username")
    print(password)

    vault.del_password(service="test_service", username="test_username")
```

`generate` params:
* `include`: The character set(s) to be used when generating the password.
  * `u`: ascii_uppercase
  * `l`: ascii_lowercase
  * `d`: digits
  * `p`: punctuation
* `exclude`: The characters to be excluded from the password.
* `length`: The number of characters our password should have.

This is not so different from `keyring`, after all, it is making use of its methods.
It exists only to serve as a base class for `KeyVault`!

</p>
</details>

---

<details>
<summary>KeyVault</summary>
<p>

This is a handler that makes use of keyring for password safe-keeping using encryption.

How to:

```python
from customlib.keyvault import KeyVault

vault = KeyVault()
vault.password(
    value=vault.generate(exclude="\'\"\\", length=16),
    salt=vault.generate(exclude="\'\"\\", length=16)
)

if __name__ == '__main__':
    vault.set_password(service="test_service", username="test_username", password="test_password")

    print(vault.get_password(service="test_service", username="test_username"))

    vault.del_password(service="test_service", username="test_username")
```

`generate` params:
* `include`: The character set(s) to be used when generating the password.
  * `u`: ascii_uppercase
  * `l`: ascii_lowercase
  * `d`: digits
  * `p`: punctuation
* `exclude`: The characters to be excluded from the password.
* `length`: The number of characters our password should have.

</p>
</details>

---

<details>
<summary>OsSleepInhibitor</summary>
<p>

With this handler we can prevent the operating system from going to sleep.

Works in `Windows` and it might work as well in `Linux` and `Darwin` systems (not tested!).

How to:

```python
from customlib.systemhandlers import OsSleepInhibitor

if __name__ == '__main__':
    with OsSleepInhibitor(keep_screen_awake=True) as osi:
        print("I just did something that took a lot of time...")
```

</p>
</details>

---

<details>
<summary>MetaSingleton</summary>
<p>

Singleton metaclass for restricting `non-strict` classes to only one instance per runtime.

How to:

```python
from customlib.singletons import MetaSingleton


class CfgParser(object, metaclass=MetaSingleton):
  """test"""


if __name__ == '__main__':
    cfg1 = CfgParser()
    cfg2 = CfgParser()

    print("*" * 80)
    print("cfg1 == cfg2:", cfg1 == cfg2)
    print("cfg1 is cfg2:", cfg1 is cfg2)
```

```
cfg1 == cfg2: True
cfg1 is cfg2: True
```

</p>
</details>

---

<details>
<summary>singleton</summary>
<p>

Singleton decorator for `metaclass`.
Restrict object to only one instance per runtime.

How to:

```python
from customlib.singletons import singleton


@singleton
class CfgParser(object):
  """test"""

  
if __name__ == '__main__':
    cfg1 = CfgParser()
    cfg2 = CfgParser()

    print("*" * 80)
    print("cfg1 == cfg2:", cfg1 == cfg2)
    print("cfg1 is cfg2:", cfg1 is cfg2)
```

```
cfg1 == cfg2: True
cfg1 is cfg2: True
```

</p>
</details>

---

<details>
<summary>NamedSingleton</summary>
<p>

Singleton decorator (for metaclass).
With this class you have the option to create multiple instances by
passing the `instance` parameter to a decorated class.

How to:

```python
from customlib.singletons import NamedSingleton


@NamedSingleton
class CfgParser(object):
  """test"""


if __name__ == '__main__':
    cfg1 = CfgParser(instance="main")
    cfg2 = CfgParser(instance="main")

    other = CfgParser(instance="other")

    print("*" * 80)
    print("cfg1 == other:", cfg1 == other)
    print("cfg1 is other:", cfg1 is other)

    print("*" * 80)
    print("cfg1 == cfg2:", cfg1 == cfg2)
    print("cfg1 is cfg2:", cfg1 is cfg2)
```

```
********************************************************************************
cfg1 == other: False
cfg1 is other: False
********************************************************************************
cfg1 == cfg2: True
cfg1 is cfg2: True
```

</p>
</details>

---

<details>
<summary>del_prefix</summary>
<p>

If `target` starts with the `prefix` string and `prefix` is not empty, return `string[len(prefix):]`.
Otherwise, return a copy of the original string.

How to:

```python
from customlib.utils import del_prefix

a = "some cool string"

if __name__ == '__main__':
    b = del_prefix(target=a, prefix="some ")
    print(b)  # --> "cool string"
```

</p>
</details>

---

<details>
<summary>del_suffix</summary>
<p>

If `target` ends with the `suffix` string and `suffix` is not empty, return `string[:-len(suffix)]`.
Otherwise, return a copy of the original string.

How to:

```python
from customlib.utils import del_suffix

a = "some cool string"

if __name__ == '__main__':
    b = del_suffix(target=a, suffix=" string")
    print(b)  # --> "some cool"
```

</p>
</details>

---

### WARNING:

As of version `v6.0.0` the following modules are no longer in this library:
* `logging` (now logpie)
* `config` (now cfgpie)
* `sqlite` (now sqlitepie)

You can install them:
```commandline
python -m pip install [--upgrade] logpie
python -m pip install [--upgrade] cfgpie
```

`sqlitepie` is not yet published.

The `logpie` library will require `customlib` & `cfgpie` as dependencies!

---

### Note:

This is still work in progress!

---
