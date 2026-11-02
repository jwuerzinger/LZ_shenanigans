'''Tree-level MSSM neutralino/chargino sector (SLHA conventions).

Basis (B~, W~3, H~d, H~u). Eigenvalues keep their sign: two states with opposite
sign have opposite CP and do not mix, so their masses can cross. That crossing is
what allows a keV-split N1/N2 pair with light gauginos.
'''

import numpy as np

MZ, MW, SW2 = 91.1876, 80.379, 0.2312
SW, CW = np.sqrt(SW2), np.sqrt(1 - SW2)
G1, G2 = 0.357, 0.652


def neutralino_matrix(M1, M2, mu, tb):
    '''Neutralino mass matrix; arguments may be broadcastable arrays -> (..., 4, 4).'''
    M1, M2, mu, tb = np.broadcast_arrays(*map(np.asarray, (M1, M2, mu, tb)))
    b = np.arctan(tb)
    cb, sb = np.cos(b), np.sin(b)
    z = np.zeros_like(M1, dtype=float)
    rows = [[M1, z, -MZ * cb * SW, MZ * sb * SW],
            [z, M2, MZ * cb * CW, -MZ * sb * CW],
            [-MZ * cb * SW, MZ * cb * CW, z, -mu],
            [MZ * sb * SW, -MZ * sb * CW, -mu, z]]
    return np.moveaxis(np.array(rows, dtype=float), (0, 1), (-2, -1))


def neutralinos(M1, M2, mu, tb):
    '''Signed eigenvalues and mixing (columns), ordered by |mass|.'''
    w, v = np.linalg.eigh(neutralino_matrix(M1, M2, mu, tb))
    o = np.argsort(np.abs(w), axis=-1)
    w = np.take_along_axis(w, o, axis=-1)
    v = np.take_along_axis(v, o[..., None, :], axis=-1)
    return w, v


def chargino_masses(M2, mu, tb):
    b = np.arctan(tb)
    X = np.array([[M2, np.sqrt(2) * MW * np.sin(b)], [np.sqrt(2) * MW * np.cos(b), mu]], dtype=float)
    return np.sort(np.linalg.svd(X, compute_uv=False))


def z_coupling(v, i, j):
    '''Z-N_i-N_j coupling relative to a pure Higgsino pair (|O_12| = 1 there).'''
    return v[..., 2, i] * v[..., 2, j] - v[..., 3, i] * v[..., 3, j]


def h_coupling(v, i, tb):
    '''Tree-level h-N_i-N_i coupling in the decoupling limit (drives elastic SI).'''
    a = np.arctan(tb) - np.pi / 2
    return (G2 * v[..., 1, i] - G1 * v[..., 0, i]) * (np.sin(a) * v[..., 2, i] + np.cos(a) * v[..., 3, i])


def crossing_function(M1, M2, mu, tb):
    '''|lightest positive eigenvalue| - |lightest negative eigenvalue|.

    Changes sign where the lightest CP-even and CP-odd neutralinos cross. Returns
    (f, is_lsp_pair): the crossing only matters when those two are N1 and N2.
    '''
    w = np.linalg.eigvalsh(neutralino_matrix(M1, M2, mu, tb))
    big = 1e12
    pos = np.where(w > 0, w, big).min(axis=-1)
    neg = np.where(w < 0, -w, big).min(axis=-1)
    third = np.sort(np.abs(w), axis=-1)[..., 2]
    return pos - neg, np.maximum(pos, neg) < third


def composition(v, i):
    return {'bino': v[..., 0, i] ** 2, 'wino': v[..., 1, i] ** 2,
            'higgsino': v[..., 2, i] ** 2 + v[..., 3, i] ** 2}
