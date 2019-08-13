###############
Getting started
###############

.. contents::
  :local:

=============
Configuration
=============

.. confval:: ros_msg_reference_version

  The used |ROS| version to use when referencing to default message types, e.g.
  ``'kinetic'`` or ``'melodic'``. It defaults to ``'melodic'`` and is set to
  ``'kinetic'`` for this documentation.

.. confval:: ros_add_package_names

  Can be set to ``False`` to prevent package names from showing in message,
  service, or action type descriptions. Defaults to ``True``.


==========
Directives
==========

.. rst:directive:: .. ros:package:: package

  Similar to the Python domain's ``.. py:module::`` directive. It will not
  output any nodes, but serves to set the context's |ROS| package and will
  produce a hyperlink target and an index entry for ``package``. Defined
  packages can be referenced with ``:ros:pkg:`package```.

  :Options: * **noindex** -- Prevents adding the package to the index,
              basically turns this directive into
              :rst:dir:`ros:currentpackage`.
            * **deprecated** -- Flags this package as deprecated. This wil
              show up in the index.


.. rst:directive:: .. ros:currentpackage:: package

  Similar to the Python domain's ``.. py:currentmodule::`` directive. It will
  not produce any nodes nor an index entry but will set the context's |ROS|
  package such that Sphinx knows that we are documenting stuff in that package.

  This directive has no options.

.. rst:directive:: .. ros:message:: message

  Can be used to describe a message type definition. It will create an index entry and a hyperlink target for this message type. It will also output nodes to describe the message.

  :options: * **noindex** -- Prevents adding the message to the index and
              creating a hyperlink target node.
            * **deprecated** -- Flags this message as deprecated. This wil show
              up in the index.

  Two flags are recognized in this directive's content: ``:msg_param <name>:``
  and ``:msg_paramtype <name>:``. The former defines a parameter that is
  contained in the message, the latter defines the same parameter's type. All
  parameters will be grouped in a list.

.. rst:directive:: .. ros:service:: service

  Can be used to describe a service type definition. It will create a hyperlink
  target for the service type. It will also output nodes to describe the
  service.

  :options: * **noindex** -- Prevents creating a hyperlink target node for the
              service.
            * **deprecated** -- Flags this service as deprecated.

  Four flags are recognized in this directive's content: ``:req_param <name>:``
  and ``:req_paramtype <name>:`` work similar to the flags of the message
  directive, but they add parameters to the service's request. ``:resp_param
  <name>:`` and ``:resp_paramtype <name>:`` do the same for the service's
  response.

.. rst:directive:: .. ros:action:: action

  Can be used to describe a action type definition. It will create a hyperlink
  target for the action type. It will also output nodes to describe the
  action.

  :options: * **noindex** -- Prevents creating a hyperlink target node for the
              action.
            * **deprecated** -- Flags this action as deprecated.

  Six flags are recognized in this directive's content: ``:goal_param <name>:``
  and ``:goal_paramtype <name>:`` work similar to the flags of the message
  directive, but they add parameters to the action's goal. ``:result_param
  <name>:`` and ``:result_paramtype <name>:`` do the same for the action's
  result. ``:feedback_param <name>:`` and ``:feedback_paramtype <name>:`` do
  the same for the action's feedback.

.. rst:directive:: .. ros:automessage:: message

  .. todo:: Add description.

  .. versionadded:: 0.2

.. rst:directive:: .. ros:autoservice:: service

  .. todo:: Add description.

  .. versionadded:: 0.2

.. rst:directive:: .. ros:autoaction:: action

  .. todo:: Add description.

  .. versionadded:: 0.2

.. rst:directive:: .. ros:autopackage:: package

  .. versionadded:: 0.2

=====
Roles
=====

.. rst:role:: ros:pkg

  Can be used to reference a defined package.

.. rst:role:: ros:msg

  Can be used to reference a defined message type. Adding the ``~`` prefix to
  the message name will let it print *only* the message name and not the
  package name. First it is checked if the message is one of the |ROS|
  primitive message types (**bool**, **int8**, **uint8**, **int16**,
  **uint16**, **int32**, **uint32**, **int64**, **uint64**, **float32**,
  **float64**, **string**, **time**, **duration**). If so, it will not link
  anywhere. If it is of the type **Header** or it is a message in one of the
  default |ROS| message packages, it will link to the proper documentation,
  keeping into account the |ROS| version set by
  :confval:`ros_msg_reference_version`.

  The default |ROS| message packages that are correctly handled as of now are:
  **std_msgs**, **geometry_msgs**, and **sensor_msgs**.

.. rst:role:: ros:srv

  Can be used to reference a defined service type. Adding the ``~`` prefix to
  the service name will let it print *only* the service name and not the
  package name.

.. rst:role:: ros:act

  Can be used to reference a defined action type. Adding the ``~`` prefix to
  the action name will let it print *only* the action name and not the package
  name.


===============
Package example
===============

.. toctree::
  :maxdepth: 1

  getting_started/full_document_example

.. literalinclude:: getting_started/full_document_example.rst
  :caption: Source
  :language: restructuredtext


=======
Indices
=======

This Sphinx extension adds two autogenerated indices. One for the
documented packages and one for the documented message types.

.. only:: html

  With the ``html`` builder, these can be referenced with ``:ref:`ros-pkgindex``` and ``:ref:`ros-msgindex```
  respectively.

  * :ref:`ros-pkgindex`
  * :ref:`ros-msgindex`

.. only:: latex

  With the ``latex`` builder, these are added automatically at the
  end of the document.
