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
cfg.parse()  # we're also parsing cmd-line args
```

- `DEFAULTS` - Holds `ConfigParser`'s default section parameters.
- `CONFIG` - Is the configuration file set by default to your project's path.
- `BACKUP` - Is the configuration default dictionary to which we fallback if the config file does not exist.

If we need to have only one instance of `CfgParser` per runtime we can use the `CfgSingleton` class
which makes use of the `singleton` design pattern and allows us to share configuration parameters
across all our python modules / packages. It is first instantiated in the `logging` module as we share
the configuration params and is referenced in `__init__.py` as simply `cfg`.

```python
from customlib import DEFAULTS, CONFIG, BACKUP
from customlib import cfg


cfg.set_defaults(**DEFAULTS)
cfg.open(file_path=CONFIG, encoding="UTF-8", fallback=BACKUP)
cfg.parse()  # we're also parsing cmd-line args
```

Because it inherits from `ConfigParser` and with the help of some extra-converters we now have
four extra methods to use in our advantage.

```python
from customlib import cfg


some_list = cfg.getlist("SECTION", "option")
some_tuple = cfg.gettuple("SECTION", "option")
some_set = cfg.getset("SECTION", "option")
some_dict = cfg.getdict("SECTION", "option")
```

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
