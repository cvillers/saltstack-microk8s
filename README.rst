salt-microk8s
=============

Statefully manage microk8s-specific features via SaltStack. For managing Kubernetes objects and resources
in a microk8s deployment, consider the builtin k8s_ or kubernetesmod_ modules.

This isn't a full-fledged formula, just a state module which can be copied to your environment.

States
------

Two states are provided: ``addon_enabled`` and ``addon_disabled``. They take one argument, ``name``,
and do exactly what they say on the tin.

Usage
-----

Place `microk8s.py <_states/microk8s.py>`_ into your ``_states`` directory, and use like this contrived example:


.. code-block:: salt

    {% set wanted_addons = ["dashboard", "rbac"] %}
    {% set unwanted_addons = ["registry"] %}

    {% for addon in wanted_addons %}
    enable_{{ addon }}:
    microk8s.addon_enabled:
        - name: {{ addon }}
    {% endfor %}

    {% for addon in unwanted_addons %}
    disable_{{ addon }}:
    microk8s.addon_disabled:
        - name: {{ addon }}
    {% endfor %}


.. _k8s: https://docs.saltstack.com/en/latest/ref/modules/all/salt.modules.k8s.html
.. _kubernetesmod: https://docs.saltstack.com/en/latest/ref/modules/all/salt.modules.kubernetesmod.html
