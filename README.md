# eopkg for Ansible

- An Ansible module to run `eopkg` commands on Solus machines
- The following `eopkg` commands can be accessed:
  - install
  - remove
  - upgrade
 - Look at `eopkg.py` for some examples

## Running this module with an Ansible playbook

- Place `eopkg.py` in a `library` directory within the same directory as `site.yml`

```text
├── library
│  ├── eopkg.py
└── site.yml
```

- Run `sudo ansible-playbook ./site.yml`

## Caveats

- **This is work-in-progress**
- Only tested locally on a Solus machine
- Definitely *not* officially supported by Solus

## Thanks

- Based on <https://github.com/ansible-collections/community.general/blob/main/plugins/modules/opkg.py>
