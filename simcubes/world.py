
import logging

from simcubes.behaviours.basebehaviour import cBehaviourHolder
from simcubes.en import Orientation
from simcubes.vec import orientation_to_vector, vector_to_orientation, make_basis, vec_to_basis

logger = logging.getLogger(__name__)


class cSimWorld:
    '''
    The whole world. A main class to generate, save, load, interact with simcubes.
    '''
    def __init__(self):
        '''
        chunks holds links to all the blocks
        active_chunk - active element from self.chunks
        '''
        self.chunks = {}
        self.active_chunk_id = None

    def set_active_chunk(self, chunk_id):
        '''
        Call this every time you switch between chunks
        :param chunk_id: active chunk id
        '''
        if not(chunk_id in self.chunks):
            self.chunks[chunk_id] = {}
        self.active_chunk_id = chunk_id

    def add_block(self, new_game_block):
        '''
        Add block to the active chunk
        :param new_game_block: a new game block, with a generated gid.
        '''
        # TODO: generate gid
        # TODO: save chunk as a reference
        new_game_block.world = self
        self.chunks[self.active_chunk_id][new_game_block.gid] = new_game_block

    def get_neighbour_cube_with_offset_direction(self, cube, direction):
        '''
        Get the neighbour to the cube in the given direction (in the active chunk)
        :param cube: some cube that's already in the world
        :param direction: find a cube in this direction (member of Orientation)
                (relative to the cube's direction), 1 step over the axis.
        :return: a cube or None
        '''
        dirvec = orientation_to_vector(direction)
        return self.get_cube_with_offset_vector(cube, dirvec)

    def get_cube_with_offset_vector(self, cube, dirvec):
        '''
        Get the neighbour to the cube in the given direction (in the active chunk)
        This does not account for cube orientation.
        :param cube: offset to this cube's coordinates
        :param dirvec: an offset vector like (1, 0, 0)
        :return: a cube or None
        '''
        thischunk = self.chunks[self.active_chunk_id]
        desired_coords = (cube.x + dirvec[0], cube.y + dirvec[1], cube.z + dirvec[2])
        # FIXME: we need a hashmap with coordinates for an active chunk
        for cube_i in thischunk.values():
            if cube_i.get_coords() == desired_coords:
                return cube_i
        return None

    def get_neighbour_by_relative_direction(self, cube, direction):
        '''
        Get the neighbour to the cube subject to it's orientation.
        :param cube: an oriented cube, offset would to this cube's
                coordinates
        :param direction: find a cube in this direction (member of Orientation)
        :return: a cube or None
        '''
        dirvec = orientation_to_vector(direction)
        return self.get_neighbour_by_relative_offset_vector(cube, dirvec)

    def get_neighbour_by_relative_offset_vector(self, cube, dirvec):
        '''
        Get the neighbour to the cube subject to it's orientation.

        dirvec is in cube's coordinates. We find the inverse transform
        into world coordinates and find the cube in world coordinates.

        :param cube: an oriented cube, offset would to this cube's
                coordinates
        :param dirvec: an offset vector like (1, 0, 0) in cube's
                coordinates
        :return: a cube or None
        '''
        Z1 = make_basis(cube.orientation, cube.rotation)
        gl_vec = vec_to_basis(dirvec, Z1)  #into world coordinates
        # now we have an offset vector in global terms
        # print(dirvec, " -> ", gl_vec)
        return self.get_cube_with_offset_vector(cube, gl_vec)

    def iter_over_blocks(self):
        '''
        Iterates over all the blocks in the world (debug purposes)
        '''
        for ch_i in self.chunks.values():
            for bl_i in ch_i.values():
                yield bl_i

    def get_debug_string(self):
        '''
        Debug only
        '''
        s = "A sim world with blocks: \n"
        for i, chunk_i in self.chunks.items():
            s += "\n*** CHUNK num" + str(i) + ":\n"
            for bl in chunk_i.values():
                s += "\t" + bl.get_debug_string() + "\n"
        return s

class cSimCube(cBehaviourHolder):
    '''
    Represents a simulation block in the game.
    Each struct GameBlock from UE4 has a link to such a simulation
    block - this makes it easy to update it.
    This thing is inherented by concrete realisations.
    '''
    def __init__(self, gid=0, x=0, y=0, z=0, cube_type=0, orientation = 0, rotation = 0):
        '''
        :param gid: game id of the block, same as in the game
        :param x, y, z: game coordinates, normalised.
        :param block_type: a string to setup behaviour
        behaviours: a list with simulation logic (read state from there)
        '''
        super().__init__()
        self.gid = gid
        self.x = x
        self.y = y
        self.z = z
        self.cube_type = cube_type
        self.orientation = orientation
        self.rotation = rotation  # 0 for "Up", heading to the sky
        self.world = None
        self.init_behaviours()

    def init_behaviours(self):
        '''
        Implement initialisation routines here. Would be called at __init__
        '''
        raise NotImplemented

    def connect(self):
        '''
        Implement behaviours connectivity here. If all you need is wall-to-wall
        connections, just implement expose_cubewall_provided_service_types and
        expose_cubewall_requested_service_types.

        If you want to do something smarter (like direct connections via tubes,
        use cBehaviourHolder.behavioural_connect_to with behaviours anyway!
        '''
        self.connect_cube_to_neighbours()

    def get_debug_string(self):
        return "Block of type " + str(self.cube_type) + " num" + str(self.gid) + " at " + str(self.x) + \
               "," + str(self.y) + "," + str(self.z) + " o:" + str(self.orientation) + " r:" + str(self.rotation)

    def set_gid(self, gid):
        self.gid = gid

    def get_coords(self):
        '''
        :return: (x, y, z) as a tuple
        '''
        return self.x, self.y, self.z

    def set_coords(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def set_orientation(self, orientation):
        self.orientation = orientation

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_z(self, z):
        self.z = z

    # Cube wall-to-wall connectivity

    def expose_cubewall_provided_service_types(self, rel_orientation):
        '''
        What kind of en.ServiceTypes does this cube provide in
        the relative location?

        Implement if-then-else here in order to automate
        connections. If you want to connect to all
        the directions, just always return the provided service.

        Default realisation - no connections in any direction.

        :param rel_orientation: en.Orientation, relative to the
                block orientation. Front is East!
        :return: list of en.ServiceTypes, there should be a bahaviour
                registered with this service type.
                Return None if there is no service provided in
                this direction.
        '''
        return None

    def expose_cubewall_requested_service_types(self, rel_orientation):
        '''
        What kind of en.ServiceTypes does this cube require in
        the relative location?

        The 'opposite' of expose_cubewall_provided_service_types.

        Default realisation - no connections in any direction.

        :param rel_orientation: en.Orientation, relative to the
                block orientation. Front is East!
        :return: list of en.ServiceTypes, there should be a bahaviour
                registered with this service type.
                Return None if there is no service provided in
                this direction.
        '''
        return None

    def connect_cube_to_neighbours(self):
        '''
        Default connectivity call. Asks expose_cubewall_provided_service_types
        and expose_cubewall_requested_service_types what kind of services
        each wall provide / request and call cBehaviourHolder.behavioural_connect_to
        if request=provide in the meeting directions.
        '''
        Z0 = make_basis(self.orientation, self.rotation)
        for rel_dir in Orientation:  # it works, don't listen to PyCharm
            # A small optimisation - no need to shake hands if we are isolated
            if (self.expose_cubewall_provided_service_types(rel_dir) is None) and \
                (self.expose_cubewall_requested_service_types(rel_dir) is None):
                continue

            # Find a neighbour
            # absolute_offset - offset in world coordinates in rel_dir relative to
            #                   this cube orientation and rotation.
            absolute_offset = vec_to_basis(orientation_to_vector(rel_dir), Z0)

            neigh_block = self.world.get_cube_with_offset_vector(self, absolute_offset)
            if neigh_block is None:
                continue
            logger.info(neigh_block.get_debug_string() + " IS " + str(rel_dir) + " REL TO " + self.get_debug_string())

            # Now we need to understand which wall is nearby - pointing to which direction?
            # Construct the basis for the other cube
            Z1 = make_basis(neigh_block.orientation, neigh_block.rotation)
            # Our rel_dir is pointing to point_vec in the other block coordinates
            point_vec = vec_to_basis(orientation_to_vector(rel_dir), Z0, Z1)
            # To find the wall that is directed on us, we need an inverse
            wall_direction = vector_to_orientation( (-point_vec[0], -point_vec[1], -point_vec[2]) )

            # Now we can shake hands over the cube walls. See the docstring in shake_hands_with_cube.
            self.shake_hands_with_cube(neigh_block, rel_dir, wall_direction)

    def shake_hands_with_cube(self, other, selfdir, otherdir):
        '''
        Call expose_cubewall_provided_service_types and expose_cubewall_requested_service_types
        to check whether they need each other.
        :param other: another cube
        :param selfdir: when looking from this cube coordinate system (defined with orientation and rotation),
                        in which direction do we see the other cube? (East is front, North is left e.t.c.)
        :param otherdir: when looking from the other cube coordinate system, in which direction do we see
                        this cube?
        '''
        logger.info(self.get_debug_string() + " MEET " + other.get_debug_string() + " WALL {0} TO {1} ".format(str(selfdir), str(otherdir)))

        i_provide = self.expose_cubewall_provided_service_types(selfdir)
        he_needs = other.expose_cubewall_requested_service_types(otherdir)
        i_need = self.expose_cubewall_requested_service_types(selfdir)
        he_provide = other.expose_cubewall_provided_service_types(otherdir)

        if not((i_need is None) or (he_provide is None)):
            for this_ser in i_need:
                for other_ser in he_provide:
                    if this_ser == other_ser:
                        logger.info(self.get_debug_string() + ' NEEDS ' + str(this_ser) + ' FROM ' + other.get_debug_string())
                        self.connect_to_another_holder(other, this_ser, other_ser)
        if not((i_provide is None) or (he_needs is None)):
            for this_ser in i_provide:
                for other_ser in he_needs:
                    if this_ser == other_ser:
                        logger.info(self.get_debug_string() + ' OFFERS ' + str(this_ser) + ' TO ' + other.get_debug_string())
                        self.connect_to_another_holder(other, this_ser, other_ser)















