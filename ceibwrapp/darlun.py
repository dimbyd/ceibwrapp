# darlun.py
'''
Creu darluniad o ddatrysiad drwy numpy a matplotlb.
'''

import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')


import cmath as cm
from datetime import datetime

from ceibwr.peiriant import Peiriant
from ceibwr.datrysiad import Datrysiad

# hyperbolic model
import geomstats.backend as gs
import geomstats.visualization as visualization
from geomstats.geometry.hyperboloid import Hyperboloid

from ceibwrapp.settings import TMP_FOLDER

plt.rcParams['font.family'] = 'monospace'


def plot(dat, hyperbolic=False, ndots=500):

    if hyperbolic:
        return plot_hyperbolic(dat, ndots=ndots)
    else:
        return plot_complex(dat, ndots=ndots)


def plot_hyperbolic(dat, ndots=100):

    # init figure
    fig = plt.figure(figsize=(6, 6))
    ax = plt.gca()

    # init hyperboloid
    h2 = Hyperboloid(dim=2)

    # atoms
    nodau = dat.nodau()
    sillafau = dat.sillafau()

    # print('nodau:', nodau)
    # print('sillafau:', sillafau)

    # plot outer circle (nodau)
    # mae'n debyg nad yw `visualisation` yn caniatau text
    # felly mae hwn yn defynddio dot mawr du am bob llythyren
    N = len(nodau)
    R = 40  # radius (???)
    dtheta = 2*np.pi/N
    pts = np.array([[R*np.sin(z), R*np.cos(z)] for z in np.arange(-np.pi/2, 3*np.pi/2, dtheta)])
    pts_int = gs.array(pts)
    pts_ext = h2.from_coordinates(pts_int, "intrinsic")
    visualization.plot(
        pts_ext,
        ax=ax,
        space="H2_poincare_disk",
        marker=".",
        color="black",
    )

    # arcs rhwng cytseiniaid (iteru dros nodau)
    for idx, nod in enumerate(nodau):
        if nod.neighbours:
            for nbr in nod.neighbours:
                idx_nbr = nodau.index(nbr)
                if idx_nbr > idx:
                    # print(idx, idx_nbr)
                    src = pts_ext[idx]
                    dst = pts_ext[idx_nbr]
                    # print('(src, dst):', (src, dst))
                
                    # disk model
                    tangent_vec = h2.metric.log(point=dst, base_point=src)
                    geodesic = h2.metric.geodesic(initial_point=src, initial_tangent_vec=tangent_vec)
                
                    arc_points = []
                    t = gs.linspace(0.0, 1.0, ndots)
                    arc_points.append(geodesic(t))
                    arc_points = gs.vstack(arc_points)
                    visualization.plot(
                        arc_points,
                        ax=ax,
                        space="H2_poincare_disk",
                        marker=".",
                        label=str('({}, {})'.format(nod, nbr))
                    )        

    # arcs rhwng odlau (iteru dros sillafau)
    for sillaf in sillafau:

        if sillaf.odl().neighbours:
            prif = sillaf.prif_lafariad()
            if prif not in nodau:
                continue
            idx = nodau.index(prif)

            for nbr in sillaf.odl().neighbours:
                nbr_prif = nbr.parent.prif_lafariad()
                if nbr_prif not in nodau:
                    continue
                idx_nbr = nodau.index(nbr_prif)

                if idx_nbr > idx:
                    # print(idx, idx_nbr)
                    src = pts_ext[idx]
                    dst = pts_ext[idx_nbr]
                    # print('(src, dst):', (src, dst))

                    # disk model
                    tangent_vec = h2.metric.log(point=dst, base_point=src)
                    geodesic = h2.metric.geodesic(initial_point=src, initial_tangent_vec=tangent_vec)

                    arc_points = []
                    t = gs.linspace(0.0, 1.0, ndots)
                    arc_points.append(geodesic(t))
                    arc_points = gs.vstack(arc_points)
                    visualization.plot(
                        arc_points,
                        ax=ax,
                        space="H2_poincare_disk",
                        marker=".",
                        label=str('({}, {})'.format(sillaf.odl(), nbr))
                    )

    # tweak
    # ax.legend(loc="center right")
    ax.set_aspect('equal')

    timestamp = datetime.timestamp(datetime.now())
    fname = 'olwyn-hyperbolic-' + str(timestamp) + ".svg"
    fname_fullpath = os.path.join(TMP_FOLDER, fname)

    fig.tight_layout()
    plt.savefig(fname_fullpath, bbox_inches='tight')

    return fname


def plot_complex(dat,  olwyn_nodau=True, ndots=1000):

    # init figure
    # fig = plt.figure(figsize=(6,6))
    # ax = plt.gca()
    # ax.cla()  # clear for fresh plot
    fig, ax = plt.subplots()

    # atoms
    nodau = dat.nodau()
    sillafau = dat.sillafau()

    # print('nodau:', nodau)
    # print('sillafau:', sillafau)

    # theta = np.linspace(0, 2*np.pi, len(nodau))  # anticlockwise
    theta = np.linspace(np.pi, -np.pi, len(nodau))  # clockwise

    # complex coords
    zpts = [complex(np.cos(arg), np.sin(arg)) for arg in theta]

    # compute toriadau (sillafau blaenorol)
    def toriadau(dat):
        if dat.lefel() == 1:
            return [corfan.sillaf_olaf() for corfan in dat.children]
        sillafau = []
        for cydran in dat.children:
            sillafau.extend(toriadau(cydran))
        return sillafau

    # helper function
    def plot_arc(ax, z1, z2, markersize=4, label=None, ndots=500):
        
        # midpt
        z = (z1 + z2)/2
        # r = abs(z1 - z)
        
        # invert
        zinv = 1/z.conjugate()
        rinv = abs(z1 - zinv)

        # args
        theta1 = cm.phase(z1 - zinv)
        theta2 = cm.phase(z2 - zinv)

        # magic
        if theta1 > theta2 and abs(theta2 - theta1) > np.pi:
            theta2 = theta2 + 2*np.pi

        args = np.linspace(theta1, theta2, ndots)
        xpts = zinv.real + rinv*np.cos(args)
        ypts = zinv.imag + rinv*np.sin(args)
        ax.plot(xpts, ypts, '.', markersize=markersize, label=label)

    # rim & spokes
    ax.plot(np.cos(theta), np.sin(theta), color='0.8', linestyle='dashed')
    for sillaf in toriadau(dat):
        idx = nodau.index(sillaf.nodau()[-1]) + 1
        ax.plot([0, zpts[idx].real], [0, zpts[idx].imag], color='0.8', linestyle='dashed')

    # connect cytseiniaid
    for idx, nod in enumerate(nodau):
        if nod.neighbours:
            for nbr in nod.neighbours:
                idx_nbr = nodau.index(nbr)
                if idx_nbr > idx:

                    label = str('{} - {}'.format(str(nod), str(nbr)))
                    plot_arc(ax, zpts[idx], zpts[idx_nbr], ndots=ndots, label=label)

    # connect sillafau
    for sillaf in sillafau:

        if sillaf.odl().neighbours:
            prif = sillaf.prif_lafariad()
            if prif not in nodau:
                continue
            idx = nodau.index(prif)

            for nbr in sillaf.odl().neighbours:
                nbr_prif = nbr.parent.prif_lafariad()
                if nbr_prif not in nodau:
                    continue
                idx_nbr = nodau.index(nbr_prif)

                if idx_nbr > idx:
                    label = str('{} - {}'.format(str(sillaf.odl()), str(nbr)))
                    plot_arc(ax, zpts[idx], zpts[idx_nbr], ndots=ndots, label=label)

    # plot olwyn nodau
    if olwyn_nodau:
        rad_olwyn = 1.05
        for arg, nod in zip(theta, nodau):
            z = rad_olwyn*complex(np.cos(arg), np.sin(arg))
            if olwyn_nodau:
                ax.text(z.real, z.imag, str(nod), rotation=np.rad2deg(arg - np.pi/2), ha="center", va="center", fontsize=10)
            else:
                ax.plot(z.real, z.imag, 'k.', markersize=10)

    # tweak
    # ax.set_xlim([-1.1, 1.1])
    # ax.set_ylim([-1.1, 1.1])
    ax.set_aspect('equal')
    ax.axis('off')
    # ax.legend(loc=(1.1, 0), markerscale=4)

    timestamp = datetime.timestamp(datetime.now())
    fname = 'olwyn-complex-' + str(timestamp) + ".svg"
    fname_fullpath = os.path.join(TMP_FOLDER, fname)

    fig.tight_layout()
    plt.savefig(fname_fullpath)

    return fname


def main():
    # input
    s = """Wele rith fel ymyl rhod - o'n cwmpas
    Campwaith dewin hynod.
    Hen linell bell nad yw'n bod
    Hen derfyn nad yw'n darfod."""

    # s = """Dwyglust feinion aflonydd
    # Dail saets wrth ei dâl y sydd
    # Trwsio fal golewo glain
    # Y bu wydrwr ei bedrain."""

    # s = """Llwybr i dranc y lle bo'r drin,
    # Diau, ni ddawr angau rin
    # Na breiniau glew na brenin."""

    # s = """Hen linell bell nad yw'n bod
    # Hen derfyn nad yw'n darfod."""

    # s = "Llewpart a dart yn ei dîn"
    # s = """Daw'n nes eiliad noswylio - i gynnau'r
    # gannwyll a machludo,
    # hunluniau ein haul yno,
    # hunluniau caeau y co'.
    # """

    # plot_hyperbolic(s)
    # plot_complex(s)

    # from datetime import datetime
    # timestamp = datetime.timestamp(datetime.now())
    
    # fname = 'olwyn-' + str(timestamp) + ".svg"
    # # fname = 'olwyn-' + str(timestamp) + ".png"
    
    pe = Peiriant()
    meta, uned = pe.parse(s)
    dat = pe.datryswr(uned)
    dat.set_nbrs()

    fname = plot(dat, ndots=500)
    print(fname)

    # fname = 'olwyn-hyperbolic-' + str(timestamp) + ".svg"
    fname = plot(s, hyperbolic=True, ndots=100)
    print(fname)


if __name__ == "__main__":
    main()
