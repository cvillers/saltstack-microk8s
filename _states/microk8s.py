# Copyright 2020 Cameron Villers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Statefully manage microk8s configuration.

:depends:    microk8s snap
:platform:   linux
"""

import logging

import salt.utils.path

_MICROK8S = "/snap/bin/microk8s"

_ACTION_STATES = {
    "enable": "enabled",
    "disable": "disabled",
}

_ACTION_OPPOSITE_STATES = {
    "enable": "disabled",
    "disabled": "enable",
}

_ACTION_CHANGED_STATES = {
    "enable": dict(old=False, new=True),
    "disable": dict(old=True, new=False),
}

log = logging.getLogger(__name__)


def _addon_enable_disable(name, action):
    """
    Helper for common enable/disable actions.

    name
        The addon name.

    action
        The action ('enable' or 'disable').
    """
    ret = {
        "name": name,
        "changes": {},
        "result": False,
        "comment": "",
    }

    # 1) Determine if the addon is already enabled, if so nothing needs to change
    current_status = __salt__["cmd.run_all"](
        "{0} status -a {1}".format(_MICROK8S, name)
    )

    log.info("current status is %r", current_status)

    # 1a) Nothing to do
    if current_status["stdout"].lower().strip() == _ACTION_STATES[action]:
        log.info("Already %s", _ACTION_STATES[action])
        ret["result"] = True
        ret["comment"] = "Addon {0} is already {1}".format(name, _ACTION_STATES[action])
        log.debug("returning %r", ret)
        return ret

    # 2) Run the enable command

    # 2a) Handle test mode
    if __opts__["test"]:
        log.info("Test mode, would %s", action)
        ret["result"] = None
        ret["comment"] = "Would {0} addon {1}".format(action, name)
        log.debug("returning %r", ret)
        return ret

    # 2b) Actually do it
    new_status = __salt__["cmd.run_all"]("{0} {1} {2}".format(_MICROK8S, action, name))
    log.info("Output from %s is %r", action, new_status)

    # 3a) Success
    if new_status["retcode"] == 0 and "is {0}".format(action) in new_status["stdout"]:
        log.info("%s successfully", _ACTION_STATES[action])
        ret["result"] = True
        ret["changes"].update(_ACTION_CHANGED_STATES[action])
        ret["comment"] = "Successfully {0} addon {1}".format(_ACTION_STATES[action], name)
    # 3b) Failure
    else:
        log.info("Could not enable")
        ret["result"] = False
        ret["comment"] = ["Could not {0} addon {1}".format(action, name)]
        ret["comment"].extend(new_status["stdout"].splitlines())

    log.info("returning %r", ret)
    return ret


def addon_enabled(name):
    """
    Enable a microk8s addon.

    name
        The addon name.
    """
    return _addon_enable_disable(name, "enable")


def addon_disabled(name):
    """
    Disable a microk8s addon.

    name
        The addon name.
    """
    return _addon_enable_disable(name, "disable")


def __virtual__():
    """
    Ensure microk8s is installed.
    """

    if salt.utils.path.which(_MICROK8S):
        return True

    return (False, "microk8s not found at {0}".format(_MICROK8S))
