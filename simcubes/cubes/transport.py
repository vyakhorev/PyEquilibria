'''
Conveyors, ?roads
'''

from simcubes.world import cSimCube
from simcubes.en import CubeTypes, AliasOrientation

from simcubes.behaviours.storage import cBehItemPullPush

class cConveyor(cSimCube):
    pass

    # def init_behaviours(self):
    #     self.cube_type = CubeTypes.blConveyor
    #     # This behaviour is registered twice. This would help other
    #     # processes to decide how to communicate with this block.
    #     beh = cBehItemPullPush(self)
    #     for serv_type in beh.get_service_types():
    #         self.register_behaviour(beh, serv_type)
    #
    # def expose_cubewall_provided_service_types(self, rel_orientation):
    #     '''
    #     This block can provide items to the front and receive items from the back
    #     '''
    #     if rel_orientation == AliasOrientation.Front:
    #         return [ServiceTypes.serProvideItems]
    #     # if rel_orientation == AliasOrientation.Back:
    #     #     return [ServiceTypes.serReceiveItems]
    #
    # def expose_cubewall_requested_service_types(self, rel_orientation):
    #     '''
    #     This block needs an item provider in the back and an item receiver in the front
    #     '''
    #     if rel_orientation == AliasOrientation.Back:
    #         # so we need someone to provide items to this block's back wall.
    #         return [ServiceTypes.serProvideItems]
    #     # if rel_orientation == AliasOrientation.Front:
    #     #     # and we need someone to receive our items from the front wall
    #     #     return [ServiceTypes.serReceiveItems]