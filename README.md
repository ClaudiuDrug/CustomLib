# customlib

A few tools for day to day work.

---

## Available tools:

<details>
<summary>CfgParser</summary>
<p>

```python
from customlib import cfg
from customlib.constants import CONFIG, DEFAULTS, BACKUP

# feed configuration parameters
cfg.set_defaults(**DEFAULTS)
cfg.open(file_path=CONFIG, encoding="UTF-8", fallback=BACKUP)

# we're parsing cmd-line arguments
cfg.parse()

# we can also do this...
# cfg.parse(["--logger-debug", "True", "--logger-handler", "console"])
```

Constants can be overridden:

- `DEFAULTS` - Holds `ConfigParser`'s default section parameters.
- `CONFIG` - Is the configuration file set by default to your project's path.
- `BACKUP` - Is the configuration default dictionary to which we fallback if the config file does not exist.

To pass cmd-line arguments:
```
D:\PyProjects\CustomLib> python -O .\script.py --section-option value --section-option value
```
cmd-line args have priority over config file and will override the cfg params.

Because it inherits from `ConfigParser` and with the help of our converters we now have
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

**Documentation is not complete...**

**More tools to be added soon...**

**Work in progress...**

---
