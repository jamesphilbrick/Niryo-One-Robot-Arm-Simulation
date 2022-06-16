# unnecessary imports commented out to improve performance

# import sys
# import copy
import time
import rospy
import moveit_commander
import geometry_msgs.msg
# import moveit_msgs.msg
# from math import pi
# from std_msgs.msg import String
# from moveit_commander.conversions import pose_to_list

# initialise
rospy.init_node('niryo_one_test', anonymous=True)
robot = moveit_commander.RobotCommander()
group_name = 'arm'
group = moveit_commander.MoveGroupCommander(group_name)
scene = moveit_commander.PlanningSceneInterface()
planning_frame = group.get_planning_frame()

eef_link = group.get_end_effector_link()
# print('end-effector link name', str(eef_link)) # debug statement

group_names = robot.get_group_names()
current_state = robot.get_current_state()
# print(str(current_state)) # debug statement
j_values = group.get_current_joint_values()


def moveIntialState(joint_goal):
    return group.go(joint_goal, wait=True)


def planPoseGoal(poseX, poseY, poseZ):

    pose_goal = geometry_msgs.msg.Pose()
    pose_goal.position.x = poseX
    pose_goal.position.y = poseY
    pose_goal.position.z = poseZ

    pose_goal.orientation.x = 0
    pose_goal.orientation.y = 0
    pose_goal.orientation.z = 0
    pose_goal.orientation.w = 1

    # print(str(pose_goal))  # debug statement

    group.set_pose_target(pose_goal)
    plan = group.go(wait=True)

    # Calling 'stop()' ensures that there is no residual movement
    group.stop()
    group.clear_pose_targets()


def unGripObject(object_name):
    scene.remove_attached_object(eef_link, name=object_name)


def gripObject(object_name):
    grasping_group = 'arm'
    touch_links = robot.get_link_names(group=grasping_group)
    scene.attach_box('tool_link', object_name, touch_links=touch_links)


def addObject(object_name, posX, posY, posZ, object_size):
    print('adding object: ', str(object_name))  # debug statement

    # initial delay to solve cinsistency issues
    if object_name == 'wall':
        rospy.sleep(0.5)

    # define object pose
    object_pose = geometry_msgs.msg.PoseStamped()
    object_pose.pose.position.x = posX
    object_pose.pose.position.y = posY
    object_pose.pose.position.z = posZ
    object_pose.pose.orientation.x = 0.0
    object_pose.pose.orientation.y = 0.0
    object_pose.pose.orientation.z = 0.0
    object_pose.pose.orientation.w = 1.0

    # print('object pose:', str(object_pose))  # debug statement

    object_pose.header.frame_id = robot.get_planning_frame()
    scene.add_box(object_name, object_pose, size=object_size)

    rospy.sleep(0.5)
    # print(scene.get_known_object_names())  # debug statement


def moveBoxStack(object_name, boxNo):
    time.sleep(0.1)
    gripObject(object_name)
    time.sleep(0.5)
    # planPoseGoal(0.0, -0.4, 0.35)  # waypoint above wall
    planPoseGoal(-0.15, -0.15, 0.05*boxNo)
    unGripObject(object_name)
    time.sleep(0.5)

    # planPoseGoal(0.0, -0.4, 0.35)  # waypoint above wall


def setup():
    box_size = (0.05, 0.05, 0.05)
    wall_size = (0.01, 1, 0.2)

    # add objects
    addObject('wall', 0.15, 0.0, 0.0, wall_size)
    addObject('box1', 0.3, -0.1, 0.0, box_size)
    addObject('box2', 0.3, 0.0, 0.0, box_size)
    addObject('box3', 0.3, 0.1, 0.0, box_size)


def cleanUp():
    print('Resetting pose and scene')
    # back to orriginal pose
    moveIntialState(j_values)

    # remove object from the scene (avoid clash if run again)
    for obj in scene.get_known_object_names():
        scene.remove_world_object(obj)


def moveBoxes():
    print('Stacking routine started')
    planPoseGoal(0.3, -0.1, 0.05)
    moveBoxStack('box1', 1)

    planPoseGoal(0.3, 0.0, 0.05)
    moveBoxStack('box2', 2)

    planPoseGoal(0.3, 0.1, 0.05)
    moveBoxStack('box3', 3)


if __name__ == '__main__':
    try:
        setup()
        moveBoxes()
        cleanUp()

    except rospy.ROSInterruptException:
        pass
