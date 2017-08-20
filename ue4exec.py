'''
This is game engine. Main entry point when we launch the simulation in-game.
Import only this file from embedded C++/Python app. to simplify things.
So we work only with the cSimulationController from UE4
'''


from controller import cSimulationController

'''
Basic game engine interface
'''

if __name__ == '__main__':
    T = 1
    dt = 0.01

    the_controller = cSimulationController()
    the_controller.generate_world()

    print("BLOCKS: ")
    for bl_i in the_controller.iterate_over_blocks():
        print(bl_i)

    print("\nSIMULATION: ")
    for t in range(0, T):
        print("-tick-"*10)
        new_events = the_controller.run_simulation_interval(dt)
        print("t={}  Events to animate {}".format(t, len(new_events)))
        for gid, role, update_data in the_controller.iterate_over_animation_updates():
            print("update of cube {} component role {} update data: {}".format(gid, role, update_data))

        print("-tock-" * 10)
