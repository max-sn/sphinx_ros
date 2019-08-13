.. ros:package:: sphinx_ros_example

###################################
The ``sphinx_ros_example`` package.
###################################

.. contents::
  :local:
  :depth: 1

The :ros:pkg:`sphinx_ros_example` package contains all sorts of ROS objects,
purely for example purposes. Objects can be referenced just like the familiar
default Sphinx references, e.g. :ros:msg:`sphinx_ros_example/Foo` will link
the proper message, and :ros:srv:`sphinx_ros_example/Bar` will link to the
proper service. We can also use the ``~`` to prevent displaying the package
name, e.g. :ros:msg:`~sphinx_ros_example/Foo` still points to the right
message.

:Author: `J. Doe <j.doe@mail.com>`_

:Maintainer: `J. Doe <j.doe@mail.com>`_

:Links: * `Repository <http://github.com/user/repo>`_
        * `Bugtracker <http://github.com/user/repo/issues>`_

:Version: 1.2

:License: MIT


************
Dependencies
************

:Build: * :ros:pkg:`message_generation`
        * :ros:pkg:`std_msgs`

:Build export: :ros:pkg:`std_msgs`

:Build tool: :ros:pkg:`catkin`

:Execution: * :ros:pkg:`message_runtime`
            * :ros:pkg:`std_msgs`


********
Messages
********

.. ros:message:: Foo

  :msg_param header: Header of the message.
  :msg_paramtype header: :ros:msg:`Header`
  :msg_param pose: The 3D pose of the foo that is detected.
  :msg_paramtype pose: :ros:msg:`geometry_msgs/Pose`
  :msg_param color: The color of the foo.
  :msg_paramtype color: :ros:msg:`string`


********
Services
********

.. ros:service:: Bar

  :req_param one_way: The request parameter.
  :req_paramtype one_way: :ros:msg:`sphinx_ros_example/Foo`
  :resp_param or_another: The response parameter.
  :resp_paramtype or_another: :ros:msg:`int8`
  :resp_param highway: The correct way.
  :resp_paramtype highway: :ros:msg:`uint16`


********
Actions
********

.. ros:action:: FooBar

  :goal_param setpoint: The setpoint to reach.
  :goal_paramtype setpoint: :ros:msg:`geometry_msgs/Point`
  :result_param steady_state_error: Error between achieved point and setpoint.
  :result_paramtype steady_state_error: :ros:msg:`geometry_msgs/Point`
  :feedback_param tracking_error: Error between ideal trajectory and current
                                  trajectory.
  :feedback_paramtype tracking_error: :ros:msg:`geometry_msgs/Point`
  :feedback_param power: Current power usage per joint.
  :feedback_paramtype power: :ros:msg:`float32[]`
