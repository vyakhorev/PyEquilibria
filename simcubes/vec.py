'''
Some basic vector calculus. Algos for tube recursive openning should
follow here as well.
'''

from simcubes.en import Orientation, Rotation

from math import cos, sin, pi
from operator import mul

# offset vectors

def orientation_to_vector(o):
    '''
    :param o: a member of Orientation
    :return: a tuple (x,y,z) directing towards the
             orientation. Like (1, 0, 0)
    '''
    if o == Orientation.West:
        return -1, 0, 0
    if o == Orientation.East:
        return 1, 0, 0
    if o == Orientation.South:
        return 0, -1, 0
    if o == Orientation.North:
        return 0, 1, 0
    if o == Orientation.Down:
        return 0, 0, -1
    if o == Orientation.Up:
        return 0, 0, 1
    raise BaseException('Unhandled direction!')

def vector_to_orientation(vec):
    '''
    :param vec: a tuple, (x, y, z), like (1, 0, 0)
    :return: a member of Orientation
    '''
    if vec == (-1, 0, 0):
        return Orientation.West
    if vec == (1, 0, 0):
        return Orientation.East
    if vec == (0, -1, 0):
        return Orientation.South
    if vec == (0, 1, 0):
        return Orientation.North
    if vec == (0, 0, -1):
        return Orientation.Down
    if vec == (0, 0, 1):
        return Orientation.Up
    raise BaseException('Unhandled direction!')

def get_opposing_direction(o):
    '''
    Useful for multiple calls wall-to-wall, easier and faster
    than vector multiplication -1 (however, that would be also
    a nice solution).
    :param o: a member of Orientation
    :return: opposing Orientation
    '''
    if o == Orientation.West:
        return Orientation.East
    if o == Orientation.East:
        return Orientation.West
    if o == Orientation.South:
        return Orientation.North
    if o == Orientation.North:
        return Orientation.South
    if o == Orientation.Down:
        return Orientation.Up
    if o == Orientation.Up:
        return Orientation.Down
    raise BaseException('Unhandled direction!')




# full transformations
# FIXME: this can be optimised a lot by doing some pre-calc

def matmul3(A, B):

    def scal(a, b):
        return sum(map(mul, a, b))

    def row(mat, i):
        return mat[i]

    def col(mat, i):
        return [r[i] for r in mat]

    Z = [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]

    for i in range(3):
        for j in range(3):
            Z[i][j] = scal(row(A, i), col(B, j))

    return Z

def matinv3(M):

    def det3(A):
        return A[0][0]*A[1][1]*A[2][2] + \
                A[0][1]*A[1][2]*A[2][0] + \
                A[0][2]*A[1][0]*A[2][1] - \
                A[0][2]*A[1][1]*A[2][0] - \
                A[0][1]*A[0][1]*A[2][2] - \
                A[0][0]*A[1][2]*A[2][1]

    C = [[0, 0, 0],
         [0, 0, 0],
         [0, 0 ,0]]

    C[0][0] = M[1][1]*M[2][2]-M[1][2]*M[2][1]
    C[0][1] = M[0][2]*M[2][1]-M[0][1]*M[2][2]
    C[0][2] = M[0][1]*M[1][2]-M[0][2]*M[1][1]
    C[1][0] = M[1][2]*M[2][0]-M[1][0]*M[2][2]
    C[1][1] = M[0][0]*M[2][2]-M[0][2]*M[2][0]
    C[1][2] = M[0][2]*M[1][0]-M[0][0]*M[1][2]
    C[2][0] = M[1][0]*M[2][1]-M[1][1]*M[2][0]
    C[2][1] = M[0][1]*M[2][0]-M[0][0]*M[2][1]
    C[2][2] = M[0][0]*M[1][1]-M[0][1]*M[1][0]

    invdet = 1 / det3(M)

    for i, row in enumerate(C):
        for j, _ in enumerate(row):
            C[i][j] = invdet * C[i][j]

    return C

def R(alpha, beta, gamma):
    rcos = lambda t: round(cos(t))
    rsin = lambda t: round(sin(t))

    def Rx(t):
        return ((1, 0, 0),
                (0, rcos(t), -rsin(t)),
                (0, rsin(t), rcos(t)))

    def Ry(t):
        return ((rcos(t), 0, rsin(t)),
                (0, 1, 0),
                (-rsin(t), 0, rcos(t)))

    def Rz(t):
        return ((rcos(t), -rsin(t), 0),
                (rsin(t), rcos(t), 0),
                (0, 0, 1))

    return matmul3(Rz(alpha), matmul3(Ry(beta), Rx(gamma)))

def orientation_to_basis(o):
    '''
    The base orientation is to the east (first axis, X).
    All the other orientation-based rotations should be
    calculated like "how do we rotate to the other direction?".

    :param o: a member of Orientation
    :return: a 3*3 matrix with orthogonal
            transition to the orientation
    '''

    # Rotation around Z axis (yaw -> alpha)

    if o == Orientation.West:
        return R(pi, 0, 0)
    if o == Orientation.East:
        # the global basis coordinates
        return ((1, 0, 0),
                (0, 1, 0),
                (0, 0, 1))
    if o == Orientation.South:
        return R(-pi / 2, 0, 0)
    if o == Orientation.North:
        return R(pi / 2, 0, 0)

    # Rotation around Y axis (pitch -> beta)

    if o == Orientation.Down:
        return R(0, -pi / 2, 0)
    if o == Orientation.Up:
        return R(0, pi / 2, 0)

def rotation_to_basis(r):
    '''
    :param r: a member of Rotation
    :return: a 3*3 matrix with orthogonal
            transition to the rotation
    '''

    # Rotation around X asis (roll -> gamma)
    if r == Rotation.Up:
        # the global basis coordinates
        return ((1, 0, 0),
                (0, 1, 0),
                (0, 0, 1))
    if r == Rotation.Right:
        return R(0, 0, pi/2)
    if r == Rotation.Down:
        return R(0, 0, pi)
    if r == Rotation.Left:
        return R(0, 0, -pi/2)

def make_basis(orientation, rotation):
    '''
    The 'normal' orientation is heading East rotated Up. So that we
    look towards increasing X axis having increasing Z above us and
    increasing Y to the left hand.

    When orientaion = East = 1, rotation = Up = 0, we have basis
    (1, 0, 0), (0, 1, 0), (0, 0, 1). In other cases we have other
    orthogonal basises (24 cases).

    :param orientation: member of Orientation
    :param rotation: member of Rotation
    :return: 3 tuples that represent the affine transition matrix from
            game coordinate system to the cube's coordinate system.
            (ok, at the moment this is a list, but we need to optimise it)
    '''
    B0 = orientation_to_basis(orientation)
    B1 = rotation_to_basis(rotation)

    return matmul3(B0, B1)

world_basis = make_basis(Orientation.East, Rotation.Up)

def vec_to_basis(vec, basis_from, basis_to=world_basis, do_round=True):
    '''
    How does a vector from basis_from basis look in basis_to basis?
    So that we do affine transform from basis_from coordinates into
    basis_to coordinates.

    :param vec: a vector to be rotated - a tuple (x,y,z)
    :param basis_from: rotate from this basis (3*3 matrix)
    :param basis_to: rotate to this basis (3*3 matrix)
    :param do_round: we have 0 and 1, so it's better to round it back
    :return: a rotated vector
    '''

    if basis_to == basis_from: return vec

    # vec~ = basis_to^-1 * basis_from * vec
    if basis_to == world_basis:
        full_transf = basis_from  # small CPU saving
    else:
        full_transf = matmul3(matinv3(basis_to), basis_from)

    scal = lambda a, b: sum(map(mul, a, b))

    new_vec = [0, 0, 0]
    for i, row_i in enumerate(full_transf):
        new_vec[i] = scal(row_i, vec)
        if do_round:
            new_vec[i] = round(new_vec[i])

    return new_vec[0], new_vec[1], new_vec[2]


if __name__ == "__main__":

    # A small test case
    B = make_basis(Orientation.Up, Rotation.Down)
    invB = matinv3(B)
    print(B)
    print(invB)
    print(matmul3(invB,B))  # should be I

    # Another test case
    B = make_basis(Orientation.North, Rotation.Up)
    print(B)
    rel_direction = [1, 0, 0]
    absolute_dir = vec_to_basis(rel_direction, B)
    print(absolute_dir)



