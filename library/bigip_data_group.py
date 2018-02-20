#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2017, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: bigip_data_group
short_description: Manage data groups on a BIG-IP
description:
  - Allows for managing data groups on a BIG-IP. Data groups provide a way to store collections
    of values on a BIG-IP for later use in things such as LTM rules, iRules, and ASM policies.
version_added: 2.6
options:
  name:
    description:
      - Specifies the name of the data group.
    required: True
  type:
    description:
      - The type of records in this data group.
      - This parameter is especially important because it causes BIG-IP to store your data
        in different ways so-as to optimize access to it. For example, it would be wrong
        to specify a list of records containing IP addresses, but label them as a C(string)
        type.
      - This value cannot be changed once the data group is created.
    choices:
      - address
      - string
      - integer
    default: string
  internal:
    description:
      - The type of this data group.
      - You should only consider setting this value in cases where you know exactly what
        you're doing, B(or), you are working with a pre-existing internal data group.
      - Be aware that if you deliberately force this parameter to C(yes), and you have a
        either a large number of records or a large total records size, this large amount
        of data will be reflected in your BIG-IP configuration. This can lead to B(long)
        system configuration load times due to needing to parse and verify the large
        configuration.
      - There is a limit of either 4 megabytes or 65,000 records (whichever is more restrictive)
        for uploads when this parameter is C(yes).
      - This value cannot be changed once the data group is created. 
    type: bool
    default: no
  external_file_name:
    description:
      - When creating a new data group, this specifies the file name that you want to give an
        external data group file on the BIG-IP.
      - This parameter is ignored when C(internal) is C(yes).
      - This parameter can be used to select an existing data group file to use with an
        existing external data group.
      - If this value is not provided, it will be given the value specified in C(name) and,
        therefore, match the name of the data group.
      - This value may only contain letters, numbers, underscores, dashes, or a period.
  records:
    description:
      - Specifies the records that you want to add to a data group.
      - If you have a large number of records, it is recommended that you use C(records_content)
        instead of typing all those records here.
      - The technical limit of either 1. the number of records, or 2. the total size of all
        records, varies with the size of the total resources on your system; in particular,
        RAM.
      - When C(internal) is C(no), at least one record must be specified in either C(records)
        or C(records_content).
    suboptions:
      key:
        description:
          - The key describing the record in the data group.
          - Your key will be used for validation of the C(type) parameter to this module.
        required: True
      value:
        description:
          - The value of the key describing the record in the data group.
  records_src:
    description:
      - Path to a file with records in it.
      - The file should be well-formed. This means that it includes records, one per line,
        that resemble the following format "key separator value". For example, C(foo := bar).
      - BIG-IP is strict about this format, but this module is a bit more lax. It will allow
        you to include arbitrary amounts (including none) of empty space on either side of
        the separator. For an illustration of this, see the Examples section.
      - Record keys are limited in length to no more than 65520 characters.
      - Values of record keys are limited in length to no more than 65520 characters.
      - The total number of records you can have in your BIG-IP is limited by the memory
        of the BIG-IP.
      - The format of this content is slightly different depending on whether you specify
        a C(type) of C(address), C(integer), or C(string). See the examples section for
        examples of the different types of payload formats that are expected in your data
        group file.
      - When C(internal) is C(no), at least one record must be specified in either C(records)
        or C(records_content).
  separator:
    description:
      - When specifying C(records_content), this is the string of characters that will
        be used to break apart entries in the C(records_content) into key/value pairs.
      - By default, this parameter's value is C(:=).
      - This value cannot be changed once it is set.
      - This parameter is only relevant when C(internal) is C(no). It will be ignored
        otherwise.
  delete_data_group_file:
    description:
      - When C(yes), will ensure that the remote data group file is deleted.
      - This parameter is only relevant when C(state) is C(absent) and C(internal) is C(no).
    default: no
    type: bool
  partition:
    description:
      - Device partition to manage resources on.
    default: Common
  state:
    description:
      - When C(state) is C(present), ensures the data group exists.
      - When C(state) is C(absent), ensures that the data group is removed.
    choices:
      - present
      - absent
extends_documentation_fragment: f5
author:
  - Tim Rupp (@caphrim007)
'''

EXAMPLES = r'''
- name: Create a data group of addresses
  bigip_data_group:
    name: foo
    password: secret
    server: lb.mydomain.com
    state: present
    user: admin
    records:
      - key: 0.0.0.0/32
        value: External_NAT
      - key: 10.10.10.10
        value: No_NAT
    type: address
  delegate_to: localhost

- name: Create a data group of strings
  bigip_data_group:
    name: foo
    password: secret
    server: lb.mydomain.com
    state: present
    user: admin
    records:
      - key: caddy
        value: ""
      - key: cafeteria
        value: ""
      - key: cactus
        value: ""
    type: string
  delegate_to: localhost

- name: Create a data group of IP addresses from a file
  bigip_data_group:
    name: foo
    password: secret
    server: lb.mydomain.com
    state: present
    user: admin
    records_src: /path/to/dg-file
    type: address
  delegate_to: localhost

- name: Update an existing internal data group of strings
  bigip_data_group:
    name: foo
    password: secret
    server: lb.mydomain.com
    state: present
    internal: yes
    user: admin
    records:
      - key: caddy
        value: ""
      - key: cafeteria
        value: ""
      - key: cactus
        value: ""
  delegate_to: localhost

- name: Show the data format expected for records_content - address
  copy:
    dest: /path/to/addresses.txt
    content: |
      network 10.0.0.0 prefixlen 8 := "Network1",
      network 172.16.0.0 prefixlen 12 := "Network2",
      network 192.168.0.0 prefixlen 16 := "Network3",
      host 192.168.20.1 := "Host1",
      host 172.16.1.1 := "Host2",

- name: Show the data format expected for records_content - string
  copy:
    dest: /path/to/strings.txt
    content: |
      a := alpha,
      b := bravo,
      c := charlie,
      x := x-ray,
      y := yankee,
      z := zulu,

- name: Show the data format expected for records_content - integer
  copy:
    dest: /path/to/integers.txt
    content: |
      1 := bar,
      2 := baz,
      3,
      4,
'''

RETURN = r'''
# only common fields returned
'''

import hashlib
import os
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback
from io import StringIO

HAS_DEVEL_IMPORTS = False

try:
    from library.module_utils.network.f5.bigip import HAS_F5SDK
    from library.module_utils.network.f5.bigip import F5Client
    from library.module_utils.network.f5.common import F5ModuleError
    from library.module_utils.network.f5.common import AnsibleF5Parameters
    from library.module_utils.network.f5.common import cleanup_tokens
    from library.module_utils.network.f5.common import fqdn_name
    from library.module_utils.network.f5.common import f5_argument_spec
    from library.module_utils.network.f5.common import iControlUnexpectedHTTPError
    HAS_DEVEL_IMPORTS = True
except ImportError:
    # Upstream Ansible
    from ansible.module_utils.network.f5.bigip import HAS_F5SDK
    from ansible.module_utils.network.f5.bigip import F5Client
    from ansible.module_utils.network.f5.common import F5ModuleError
    from ansible.module_utils.network.f5.common import AnsibleF5Parameters
    from ansible.module_utils.network.f5.common import cleanup_tokens
    from ansible.module_utils.network.f5.common import fqdn_name
    from ansible.module_utils.network.f5.common import f5_argument_spec
    from ansible.module_utils.network.f5.common import iControlUnexpectedHTTPError

try:
    import netaddr
    HAS_NETADDR = True
except ImportError:
    HAS_NETADDR = False


class ContentValidator(object):
    def __init__(self, content, separator, type):
        """Create instance of ContentValidator

        External data-groups will usually provide a StringIO object where-as the Internal
        data-groups are usually represented by lists. Either of them can be iterated over.

        Args:
            content (iterable): The data to iterate over looking for discrepancies in.
            type (string): The proposed type of data that is sent to the module. The
                content will be checked against this type to ensure it is correct.
        """
        self._content = content
        self._separator = separator
        self._type = type
        self._invalid_line = 0

    def is_valid(self):
        self._content.seek(0)
        if self._type == 'ip':
            result = self._is_valid_address()
        elif self._type == 'integer':
            result = self._is_valid_integer()
        else:
            result = self._is_valid_string()
        self._content.seek(0)
        return result

    def _is_valid_string(self):
        for line in self._content:
            line = line.strip().strip(',')
            if line == "":
                continue
            self._invalid_line += 1
            key, value = line.split(self._separator)
            key = key.strip()
            try:
                netaddr.IPNetwork(key)
                return False
            except netaddr.core.AddrFormatError:
                pass
            try:
                int(key)
                return False
            except ValueError:
                pass
        return True

    def _is_valid_address(self):
        for line in self._content:
            line = line.strip().strip(',')
            if line == "":
                continue
            self._invalid_line += 1
            if self._is_valid_network_address(line):
                continue
            elif self._is_valid_host_address(line):
                continue
            return False
        return True

    def _is_valid_network_address(self, line):
        pattern = r'^network\s+(?P<addr>[^ ]+)\s+prefixlen\s+(?P<prefix>\d+)\s+.*'
        matches = re.match(pattern, line)
        if matches:
            address = matches.group('addr').strip()
            prefixlen = matches.group('prefix').strip()
            cidr = '{0}/{1}'.format(address, prefixlen)
            try:
                netaddr.IPNetwork(cidr)
                return True
            except netaddr.core.AddrFormatError:
                pass
        return False

    def _is_valid_host_address(self, line):
        pattern = r'^host\s+(?P<addr>[^ ]+)\s+.*'
        matches = re.match(pattern, line)
        if matches:
            try:
                netaddr.IPNetwork(matches.group('addr'))
                return True
            except netaddr.core.AddrFormatError:
                pass
        return False

    def _is_valid_integer(self):
        for line in self._content:
            line = line.strip().strip(',')
            if line == "":
                continue
            self._invalid_line += 1
            try:
                int(line)
                return True
            except ValueError:
                pass
            key, value = line.split(self._separator)
            key = key.strip()
            try:
                int(key)
            except ValueError:
                return False
        return True

    @property
    def invalid_line(self):
        return self._invalid_line


class Parameters(AnsibleF5Parameters):
    api_map = {}

    api_attributes = [
        'records', 'type'
    ]

    returnables = []

    @property
    def type(self):
        if self._values['type'] in ['address', 'addr', 'ip']:
            return 'ip'
        elif self._values['type'] in ['integer', 'int']:
            return 'integer'
        else:
            return 'string'


class InternalApiParameters(Parameters):
    updatables = [
        'records'
    ]

    @property
    def records(self):
        pass


class ExternalApiParameters(Parameters):
    api_map = {
        'externalFileName': 'external_file_name'
    }

    updatables = [
        'checksum'
    ]

    @property
    def checksum(self):
        if self._values['checksum'] is None:
            return None
        result = self._values['checksum'].split(':')[2]
        return result


class InternalModuleParameters(Parameters):
    @property
    def records(self):

    @property
    def records_stringio(self):
        if self._values['records_stringio']:
            return self._values['records_stringio']
        if self._values['records_content'] is None:
            result = self._convert_records_list_to_string(self._values['records'])
            result = StringIO(u"{0}".format(result))
        else:
            result = StringIO(u"{0}".format(self._values['records_content']))
        self._values['records_stringio'] = result
        return result

    def _convert_records_list_to_string(self, contents):
        """Converts a list of record dicts to a string

        Args:
            contents (list): The list of k/v records to convert.

        Returns:
            string: The string that the k/v records was converted to.
        """
        result = []
        if len(contents) == 1 and contents[0] == "":
            return ""
        for content in contents:
            addr = netaddr.IPNetwork(content['key'])
            if 'key' in content and 'value' in content:
                if addr.prefixlen in [32, 128]:
                    line = 'host {0} {1} {2},'.format(
                        content['key'], self.separator, content['value']
                    )
                else:
                    line = 'network {0} prefixlen {1} {2} {3},'.format(
                        str(addr.network), str(addr.prefixlen), self.separator,
                        content['value']
                    )
            elif 'key' in content:
                if addr.prefixlen in [32, 128]:
                    line = 'host {0} {1} "",'.format(
                        content['key'], self.separator
                    )
                else:
                    line = 'network {0} prefixlen {1} {2} "",'.format(
                        str(addr.network), str(addr.prefixlen), self.separator
                    )
            else:
                raise F5ModuleError(
                    "You must specify at least a 'key' when specifying a list of records."
                )
            result.append(line)
        result = "\n".join(result)
        return result


class ExternalModuleParameters(Parameters):
    @property
    def checksum(self):
        if self._values['checksum']:
            return self._values['checksum']
        result = hashlib.sha1(self.records_stringio.getvalue())
        result = result.hexdigest()
        self._values['checksum'] = result
        return result

    @property
    def external_file_name(self):
        if self._values['external_file_name'] is None:
            name = self.name
        else:
            name = self._values['external_file_name']
        if re.search(r'[^a-z0-9-_.]', name):
            raise F5ModuleError(
                "'external_file_name' may only contain letters, numbers, underscores, dashes, or a period."
            )
        return name

    @property
    def records_stringio(self):
        if self._values['records_stringio']:
            return self._values['records_stringio']
        if self._values['records_content'] is None:
            result = self._convert_records_list_to_string(self._values['records'])
            result = StringIO(u"{0}".format(result))
        else:
            result = StringIO(u"{0}".format(self._values['records_content']))
        self._values['records_stringio'] = result
        return result

    def _convert_records_list_to_string(self, contents):
        """Converts a list of record dicts to a string

        Args:
            contents (list): The list of k/v records to convert.

        Returns:
            string: The string that the k/v records was converted to.
        """
        result = []
        if len(contents) == 1 and contents[0] == "":
            return ""
        for content in contents:
            if 'key' in content and 'value' in content:
                line = "{0} {1} {2},".format(content['key'], self.separator, content['value'])
            elif 'key' in content:
                line = "{0},".format(content['key'])
            else:
                raise F5ModuleError(
                    "You must specify at least a 'key' when specifying a list of records."
                )
            result.append(line)
        result = "\n".join(result)
        return result


class Changes(Parameters):
    def to_return(self):
        result = {}
        try:
            for returnable in self.returnables:
                result[returnable] = getattr(self, returnable)
            result = self._filter_params(result)
        except Exception:
            pass
        return result


class UsableChanges(Changes):
    pass


class ReportableChanges(Changes):
    pass


class Difference(object):
    def __init__(self, want, have=None):
        self.want = want
        self.have = have

    def compare(self, param):
        try:
            result = getattr(self, param)
            return result
        except AttributeError:
            return self.__default(param)

    def __default(self, param):
        attr1 = getattr(self.want, param)
        try:
            attr2 = getattr(self.have, param)
            if attr1 != attr2:
                return attr1
        except AttributeError:
            return attr1

    @property
    def checksum(self):
        if self.want.checksum != self.have.checksum:
            return True


class BaseManager(object):
    def __init__(self, *args, **kwargs):
        self.module = kwargs.get('module', None)
        self.client = kwargs.get('client', None)

    def _set_changed_options(self):
        changed = {}
        for key in Parameters.returnables:
            if getattr(self.want, key) is not None:
                changed[key] = getattr(self.want, key)
        if changed:
            self.changes = UsableChanges(params=changed)

    def _update_changed_options(self):
        diff = Difference(self.want, self.have)
        updatables = Parameters.updatables
        changed = dict()
        for k in updatables:
            change = diff.compare(k)
            if change is None:
                continue
            else:
                if isinstance(change, dict):
                    changed.update(change)
                else:
                    changed[k] = change
        if changed:
            self.changes = UsableChanges(params=changed)
            return True
        return False

    def should_update(self):
        result = self._update_changed_options()
        if result:
            return True
        return False

    def exec_module(self):
        changed = False
        result = dict()
        state = self.want.state

        try:
            if state == "present":
                changed = self.present()
            elif state == "absent":
                changed = self.absent()
        except iControlUnexpectedHTTPError as e:
            raise F5ModuleError(str(e))

        reportable = ReportableChanges(params=self.changes.to_return())
        changes = reportable.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        self._announce_deprecations(result)
        return result

    def _announce_deprecations(self, result):
        warnings = result.pop('__warnings', [])
        for warning in warnings:
            self.client.module.deprecate(
                msg=warning['msg'],
                version=warning['version']
            )

    def present(self):
        if self.exists():
            return self.update()
        else:
            return self.create()

    def update(self):
        self.have = self.read_current_from_device()
        if not self.should_update():
            return False
        if self.module.check_mode:
            return True
        self.update_on_device()
        return True

    def absent(self):
        if self.exists():
            return self.remove()
        return False


class InternalManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super(InternalManager, self).__init__(*args, **kwargs)
        self.want = InternalModuleParameters(params=self.module.params)
        self.have = InternalApiParameters()
        self.changes = UsableChanges()

    def _content_size_is_too_big(self):
        records = self.want.records_stringio
        records.seek(0, os.SEEK_END)
        size = records.tell()
        records.seek(0)
        if size > 4000000:
            return True
        records.seek(0)
        return False

    def _too_many_lines(self):
        result = False
        seek_cur = self.want.records_stringio.tell()
        for i, line in enumerate(self.want.records_stringio):
            if i > 65000:
                result = True
        self.want.records_stringio.seek(seek_cur)
        return result

    def remove(self):
        if self.module.check_mode:
            return True
        self.remove_from_device()
        if self.exists():
            raise F5ModuleError("Failed to delete the resource.")
        return True

    def create(self):
        self._set_changed_options()
        if self._content_size_is_too_big() or self._too_many_lines():
            raise F5ModuleError(
                "The size of the provided data (or file) is too large for an internal data group."
            )
        validator = ContentValidator(
            self.want.records_stringio, self.want.separator, self.want.type
        )
        if not validator.is_valid():
            raise F5ModuleError(
                "The value on line '{0}' does not match the type '{1}'".format(
                    validator.invalid_line, self.want.type
                )
            )
        if self.module.check_mode:
            return True
        self.create_on_device()
        return True

    def exists(self):
        result = self.client.api.tm.ltm.data_group.internals.internal.exists(
            name=self.want.name,
            partition=self.want.partition
        )
        return result

    def create_on_device(self):
        params = self.want.api_params()
        self.client.api.tm.ltm.data_group.internals.internal.create(
            name=self.want.name,
            partition=self.want.partition,
            **params
        )

    def update_on_device(self):
        params = self.want.api_params()
        resource = self.client.api.tm.ltm.data_group.internals.internal.load(
            name=self.want.name,
            partition=self.want.partition
        )
        resource.modify(**params)

    def remove_from_device(self):
        resource = self.client.api.tm.ltm.data_group.internals.internal.load(
            name=self.want.name,
            partition=self.want.partition
        )
        if resource:
            resource.delete()

    def read_current_from_device(self):
        resource = self.client.api.tm.ltm.data_group.internals.internal.load(
            name=self.want.name,
            partition=self.want.partition
        )
        result = resource.attrs
        return InternalApiParameters(params=result)


class ExternalManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super(ExternalManager, self).__init__(*args, **kwargs)
        self.want = ExternalModuleParameters(params=self.module.params)
        self.have = ExternalApiParameters()
        self.changes = UsableChanges()

    def absent(self):
        result = False
        if self.exists():
            result = self.remove()
        if self.external_file_exists() and self.want.delete_data_group_file:
            result = self.remove_data_group_file_from_device()
        return result

    def remove(self):
        if self.module.check_mode:
            return True
        self.remove_from_device()
        if self.exists():
            raise F5ModuleError("Failed to delete the resource.")
        return True

    def create(self):
        self._set_changed_options()
        validator = ContentValidator(
            self.want.records_stringio, self.want.separator, self.want.type
        )
        if not validator.is_valid():
            raise F5ModuleError(
                "The value on line '{0}' does not match the type '{1}'".format(
                    validator.invalid_line, self.want.type
                )
            )
        if self.module.check_mode:
            return True
        self.create_on_device()
        return True

    def exists(self):
        result = self.client.api.tm.ltm.data_group.externals.external.exists(
            name=self.want.name,
            partition=self.want.partition
        )
        return result

    def external_file_exists(self):
        result = self.client.api.tm.sys.file.data_groups.data_group.exists(
            name=self.want.external_file_name,
            partition=self.want.partition
        )
        return result

    def _is_zero_length_file(self):
        current = self.want.records_stringio.tell()
        self.want.records_stringio.seek(0, os.SEEK_END)
        length = self.want.records_stringio.tell()
        self.want.records_stringio.seek(current)
        if length == 0:
            return True
        return False

    def _upload_to_file(self, name, type, remote_path, update=False):
        if self._is_zero_length_file():
            raise F5ModuleError(
                "External data groups may not be empty"
            )

        self.client.api.shared.file_transfer.uploads.upload_stringio(
            self.want.records_stringio, name
        )
        resource = self.client.api.tm.sys.file.data_groups
        if update:
            resource = resource.data_group.load(
                name=name,
                partition=self.want.partition
            )
            resource.modify(
                sourcePath='file:{0}'.format(remote_path)
            )
            resource.refresh()
            result = resource
        else:
            result = resource.data_group.create(
                name=name,
                type=type,
                sourcePath='file:{0}'.format(remote_path)
            )
        return result.name

    def create_on_device(self):
        name = self.want.external_file_name
        remote_path = '/var/config/rest/downloads/{0}'.format(name)
        external_file = self._upload_to_file(
            name, self.want.type, remote_path, update=False
        )
        self.client.api.tm.ltm.data_group.externals.external.create(
            name=self.want.name,
            partition=self.want.partition,
            externalFileName=external_file
        )
        self.client.api.tm.util.unix_rm.exec_cmd('run', utilCmdArgs=remote_path)

    def update_on_device(self):
        name = self.want.external_file_name
        remote_path = '/var/config/rest/downloads/{0}'.format(name)
        external_file = self._upload_to_file(
            name, self.have.type, remote_path, update=True
        )
        resource = self.client.api.tm.ltm.data_group.externals.external.load(
            name=self.want.name,
            partition=self.want.partition
        )
        resource.modify(
            externalFileName=external_file
        )

    def remove_from_device(self):
        resource = self.client.api.tm.ltm.data_group.externals.external.load(
            name=self.want.name,
            partition=self.want.partition
        )
        if resource:
            resource.delete()

        # Remove the remote data group file if asked to
        if self.want.delete_data_group_file:
            self.remove_data_group_file_from_device()

    def remove_data_group_file_from_device(self):
        resource = self.client.api.tm.sys.file.data_groups.data_group.load(
            name=self.want.external_file_name,
            partition=self.want.partition
        )
        if resource:
            resource.delete()
            return True
        return False

    def read_current_from_device(self):
        """Reads the current configuration from the device

        For an external data group, we are interested in two things from the
        current configuration

        * ``checksum``
        * ``type``

        The ``checksum`` will allow us to compare the data group value we have
        with the data group value being provided.

        The ``type`` will allow us to do validation on the data group value being
        provided (if any).

        Returns:
             ExternalApiParameters: Attributes of the remote resource.
        """
        resource = self.client.api.tm.ltm.data_group.externals.external.load(
            name=self.want.name,
            partition=self.want.partition
        )
        external_file = os.path.basename(resource.externalFileName)
        external_file_partition = os.path.dirname(resource.externalFileName).strip('/')
        resource = self.client.api.tm.sys.file.data_groups.data_group.load(
            name=external_file,
            partition=external_file_partition
        )
        result = resource.attrs
        return ExternalApiParameters(params=result)


class ModuleManager(object):
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.module = kwargs.get('module')
        self.client = kwargs.get('client', None)

    def exec_module(self):
        if self.module.params['internal']:
            manager = self.get_manager('internal')
        else:
            manager = self.get_manager('external')
        return manager.exec_module()

    def get_manager(self, type):
        if type == 'internal':
            return InternalManager(**self.kwargs)
        elif type == 'external':
            return ExternalManager(**self.kwargs)


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        argument_spec = dict(
            name=dict(required=True),
            type=dict(
                choices=['address', 'addr', 'ip', 'string', 'str', 'integer', 'int'],
                default='string'
            ),
            delete_data_group_file=dict(type='bool'),
            internal=dict(type='bool', default='no'),
            records=dict(
                type='list',
                suboptions=dict(
                    key=dict(required=True),
                    value=dict(type='raw')
                )
            ),
            records_src=dict(type='path'),
            external_file_name=dict(),
            separator=dict(default=':='),
            state=dict(choices=['absent', 'present'], default='present'),
            partition=dict(
                default='Common',
                fallback=(env_fallback, ['F5_PARTITION'])
            )
        )
        self.argument_spec = {}
        self.argument_spec.update(f5_argument_spec)
        self.argument_spec.update(argument_spec)
        self.mutually_exclusive = [
            ['records', 'records_content', 'external_file_name']
        ]


def main():
    spec = ArgumentSpec()

    module = AnsibleModule(
        argument_spec=spec.argument_spec,
        supports_check_mode=spec.supports_check_mode
    )
    if not HAS_F5SDK:
        module.fail_json(msg="The python f5-sdk module is required")
    if not HAS_NETADDR:
        module.fail_json(msg="The python netaddr module is required")

    try:
        client = F5Client(**module.params)
        mm = ModuleManager(module=module, client=client)
        results = mm.exec_module()
        cleanup_tokens(client)
        module.exit_json(**results)
    except F5ModuleError as ex:
        cleanup_tokens(client)
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()
