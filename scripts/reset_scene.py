import rospy
import moveit_commander

rospy.init_node('niryo_one_test', anonymous=True)
robot = moveit_commander.RobotCommander()
group_name = 'arm'
group = moveit_commander.MoveGroupCommander(group_name)
scene = moveit_commander.PlanningSceneInterface()

j_values = [0.0, 0.640187, -1.397485, 0.0, 0.0, 0.0]

if __name__ == "__main__":
    try:
        group.go(j_values, wait=True)
        for obj in scene.get_known_object_names():
            scene.remove_world_object(obj)
    except rospy.ROSInterruptException:
        pass
