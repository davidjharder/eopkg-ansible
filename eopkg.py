#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, David Harder <david@davidjharder.ca>
# Heavily based on opkg module by Patrick Pelletier (@skinp)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: eopkg
author: "David Harder"
short_description: Package manager for Solus
description:
    - Manages packages for Solus
options:
    name:
        description:
            - Name of package(s) to install/remove.
        aliases: [pkg] TODO: what is aliases?
        required: true TODO can this be removed
        type: list
        elements: str
    state:
        description:
            - State of the package.
        choices: [ 'present', 'absent', 'installed', 'removed' ]
        default: present
        type: str
    update_installed_packages:
        description:
            - Update packages already installed.
        default: false
        type: bool
requirements:
    - eopkg
"""
EXAMPLES = """
- name: Install foo
  community.general.eopkg:
    name: foo
    state: present

- name: Remove foo
  community.general.eopkg:
    name: foo
    state: absent

- name: Remove foo and bar
  community.general.eopkg:
    name:
      - foo
      - bar
    state: absent
- name: Update packages
  community.general.eopkg:
    update_installed_packages: true
    name: foo
    state: present
TODO: for now a name (package) is required even for an update
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import shlex_quote


def update_installed_packages(module, eopkg_path):
    """Update packages already installed."""

    rc, out, err = module.run_command("%s upgrade -y" % eopkg_path)

    if rc != 0:
        module.fail_json(msg="Could not update installed packages")


def query_package(module, eopkg_path, name, state="present"):
    """Returns whether a package is installed or not."""

    if state == "present":

        rc, out, err = module.run_command(
            '%s info %s | grep -q "Installed package"'
            % (shlex_quote(eopkg_path), shlex_quote(name)),
            use_unsafe_shell=True,
        )
        if rc == 0:
            return True

        return False


def remove_packages(module, eopkg_path, packages):
    """Uninstalls one or more packages if installed."""

    remove_c = 0
    # Using a for loop in case of error, we can report the package that failed
    for package in packages:
        # Query the package first, to see if we even need to remove
        if not query_package(module, eopkg_path, package):
            continue

        rc, out, err = module.run_command("%s remove %s -y" % (eopkg_path, package))

        if query_package(module, eopkg_path, package):
            module.fail_json(msg="Failed to remove %s: %s" % (package, out))

        remove_c += 1

    if remove_c > 0:

        module.exit_json(changed=True, msg="removed %s package(s)" % remove_c)

    module.exit_json(changed=False, msg="package(s) already absent")


def install_packages(module, eopkg_path, packages):
    """Installs one or more packages if not already installed."""

    install_c = 0

    for package in packages:
        if query_package(module, eopkg_path, package):
            continue

        rc, out, err = module.run_command("%s install %s -y" % (eopkg_path, package))

        if not query_package(module, eopkg_path, package):
            module.fail_json(msg="Failed to install %s: %s" % (package, out))

        install_c += 1

    if install_c > 0:
        module.exit_json(changed=True, msg="installed %s package(s)" % (install_c))

    module.exit_json(changed=False, msg="package(s) already present")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=["pkg"], required=True, type="list", elements="str"),
            state=dict(
                default="present", choices=["present", "installed", "absent", "removed"]
            ),
            update_installed_packages=dict(default=False, type="bool"),
        )
    )

    eopkg_path = module.get_bin_path("eopkg", True, ["/usr/bin"])

    p = module.params

    if p["update_installed_packages"]:
        update_installed_packages(module, eopkg_path)

    pkgs = p["name"]

    if p["state"] in ["present", "installed"]:
        install_packages(module, eopkg_path, pkgs)

    elif p["state"] in ["absent", "removed"]:
        remove_packages(module, eopkg_path, pkgs)


if __name__ == "__main__":
    main()
