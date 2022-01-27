# customlib

A few tools for day to day work.

---

## Available tools:

<details>
<summary>CfgParser & CfgSingleton</summary>
<p>

```python
from customlib import DEFAULTS, CONFIG, BACKUP
from customlib.cfgparser import CfgParser


cfg = CfgParser()
cfg.set_defaults(**DEFAULTS)
cfg.open(file_path=CONFIG, encoding="UTF-8", fallback=BACKUP)
cfg.parse()
```

- `DEFAULTS` - Holds `ConfigParser`'s default section parameters.
- `CONFIG` - Is the configuration file set by default to your project's path.
- `BACKUP` - Is the configuration default dictionary to which we fallback if the config file does not exist.

If we need to have only one instance of `CfgParser` per runtime we can use the `CfgSingleton` class
which makes use of the `singleton` design pattern and allows us to share configuration parameters
across all our python modules / packages.

```python
from customlib import DEFAULTS, CONFIG, BACKUP
from customlib.cfgparser import CfgSingleton


cfg = CfgSingleton()  # restricted to one instance per runtime
cfg.set_defaults(**DEFAULTS)
cfg.open(file_path=CONFIG, encoding="UTF-8", fallback=BACKUP)
cfg.parse()
```

Works and accepts `*args` & `**kwargs` exactly as `ConfigParser`.
The configuration files are read & written using `FileHandle` (see `customlib.handles`),
a custom context-manager with thread & file locking abilities.

</p>
</details>

---

## NOTE:

Documentation is not yet complete...
More tools to be added soon...

**Work in progress...**

---
