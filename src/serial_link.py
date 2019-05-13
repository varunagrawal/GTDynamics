"""
Test forward dynamics using factor graphs.
Author: Frank Dellaert and Mandy Xie

We follow Lynch & Park 2017 conventions, but using j to index joints, as in Corke 2017:
    - j=0 is base
    - j in 1...N index joints
    - Mj is COM pose of link j in base frame 0.
    - Tj is the link frame j, aligned with joint j+1, expressed in base frame 0.
    - we use shorthand i==j-1 and k==j+1
"""

# pylint: disable=C0103, E1101, E0401, C0412

from __future__ import print_function

import numpy as np

import gtsam
import utils
from gtsam import Pose3, Rot3
from link import Link, V, a, t

ZERO6 = utils.vector(0, 0, 0, 0, 0, 0)


class SerialLink(object):
    """
        Calculate forward dynamics for manipulator using factor graph method
    """

    def __init__(self, calibration, base=Pose3(), tool=Pose3()):
        """ Constructor serial link manipulator from list of Link instances.
            Keyword arguments:
                calibration -- Link list
                base        -- optional wT0 base frame in world frame
                tool        -- optional tool frame in link N frame
        """
        self._links = calibration
        self._base = base
        self._tool = tool

        # Calculate screw axes for all joints, expressed in their COM frame.
        self._screw_axes = [link.screw_axis for link in self._links]

    @classmethod
    def from_urdf(cls, urdf_link_dict: dict, leaf_link_name: str):
        """ Construct from data structure produced by read_urdf.

        Arguments:
            urdf_link_dict {dict} -- map from name -> [URDFLink, parent]
            leaf_link_name {str} -- name for the leaf link.

        Returns:
            SerialLink -- instance of SerialLink with one chain
        """

        # TODO(yetong): build the links in a tree structure
        # The serial link class only supports serial connection (one child policy).
        # However, there may be several children connected to the parent in the fetch robot, 
        # and the links form a tree structure.
        # Currently, I only choose one path in the tree structure, and build a serial link

        link_name = leaf_link_name
        urdf_links = []

        # find the links connecting leaf_link to base_link
        while link_name in urdf_link_dict:
            urdf_link, parent_name = urdf_link_dict[link_name]
            urdf_links = [urdf_link] + urdf_links
            link_name = parent_name
        return cls(urdf_links)

    @property
    def base(self):
        """Return base pose in world frame."""
        return self._base

    def link(self, i):
        """Return link[i], base 0."""
        return self._links[i]

    @property
    def tool(self):
        """Return tool pose in link N frame."""
        return self._tool

    @property
    def num_links(self):
        """Return number of *moving* links."""
        return len(self._links)

    def link_transforms(self, q=None):
        """ Calculate link transforms for all links.
            Keyword arguments:
                q (numpy array) -- optional joint angles (default all zero).
        """
        return [link.A(0 if q is None else q[i]) for i, link in enumerate(self._links)]

    def fkine(self, q=None):
        """ Forward kinematics.
            Keyword arguments:
                q (numpy array) -- joint angles.
            Returns tool frame in world frame.
        """
        t = self._base
        for A in self.link_transforms(q):
            t = t.compose(A)
        return t.compose(self._tool)

    def link_frames(self, q=None):
        """ Return each link frame for given joint angles.
            Note that frame Tj is aligned with the joint axis of joint j+1
            according to the Denavit-Hartenberg convention.
            Keyword arguments:
                q (numpy array) -- optional joint angles (default all zero).
            Returns tool frame in world frame.
        """
        frames = []
        t = self._base
        for A in self.link_transforms(q):
            t = t.compose(A)
            frames.append(t)
        return frames

    def com_frames(self, q=None):
        """ Return each link's center of mass frame at rest, in the world frame."""
        t = self._base
        frames = []
        for i, A in enumerate(self.link_transforms(q)):
            t = t.compose(A)
            iTcom = self.link(i).center_of_mass
            frames.append(utils.compose(t, iTcom))
        return frames

    def screw_axes(self):
        """Return screw axes for all joints, expressed in their COM frame."""
        return self._screw_axes

    def twists(self, Ts, joint_velocities):
        """ Return velocity twists for all joints, expressed in their COM frame.
            Keyword arguments:
                Ts -- com frames
                joint velocities (np.array, in rad/s)
        """
        # TODO(Frank): take jTi list instead, or better: do jTi with exp
        # The first link's twist is just from the joint
        twists = [self._screw_axes[0] * joint_velocities[0]]

        # Loop over joints j>1
        for j in range(2, self.num_links + 1):
            # Equation 8.45 in MR, page 292
            twist_i = twists[-1]
            jTi = Ts[j - 1].between(Ts[j - 2])
            Aj = self._screw_axes[j - 1]
            joint_vel_j = joint_velocities[j - 1]
            twist_j = np.dot(jTi.AdjointMap(), twist_i) + Aj * joint_vel_j
            twists.append(twist_j)

        return twists

    def twists_gtsam(self, q, joint_velocities):
        """ Return velocity twists for all joints, expressed in their COM frame.
            This version uses GTSAM, mainly used to test twist factors.
            Keyword arguments:
                q (np.array, in rad) - joint angles
                joint velocities (np.array, in rad/s)
        """
        # configuration of link frame j-1 relative to link frame j for arbitrary joint angle
        jTis = self.jTi_list(q)

        gfg = gtsam.GaussianFactorGraph()

        # Add factor for each joint
        for i, (link, jTi, joint_vel_j) in enumerate(zip(self._links, jTis, joint_velocities)):
            gfg.add(link.twist_factor(i + 1, jTi, joint_vel_j))

        result = gfg.optimize()
        return [result.at(V(j)) for j in range(1, self.num_links + 1)]

    def jTi_list(self, q):
        """ Calculate list of transforms from COM frame j-1 relative to COM j.
            Keyword arguments:
                q (np.array, in rad) - joint angles
            Returns list of transforms, 2 more than number of links:
                - first transform is bT1, i.e. base expressed in link 1
                - last transform is tTnc, i.e., link N COM frame expressed in tool frame
        """
        # TODO(Frank): I don't like these inverses, wished we could do with forward.
        Ts = self.com_frames(q)
        bT1 = Ts[0].between(self._base)
        nTt = self.tool
        nTc = self._links[-1].center_of_mass
        tTnc = nTt.between(nTc)
        return [bT1] + [Tj.between(Ti) for Ti, Tj in zip(Ts[:-1], Ts[1:])] + [tTnc]

    def forward_factor_graph(self, q, joint_velocities, torques,
                             gravity=None, base_twist_accel=ZERO6, external_wrench=ZERO6):
        """ Build factor graph for solving forward dynamics.
            Keyword arguments:
                q (np.array, in rad) - joint angles
                joint velocities (np.array, in rad/s)
                torques (np.array, in Nm)
                gravity (np.array) -- if given, will create gravity forces
                base_twist_accel (np.array) -- optional acceleration to force at base
                external_wrench (np.array) -- optional external wrench
            Returns Gaussian factor graph
        """
        N = self.num_links
        assert q.shape == (N,)
        assert joint_velocities.shape == (N,)
        assert torques.shape == (N,)

        # configuration of COM link frames
        Ts = self.com_frames(q)

        # Calculate all twists
        twists = self.twists(Ts, joint_velocities)

        # Set up Gaussian Factor Graph
        gfg = gtsam.GaussianFactorGraph()

        # Add factor to enforce base acceleration equal to zero
        gfg.add(Link.base_factor(base_twist_accel))

        # configuration of link frame j-1 relative to link frame j for arbitrary joint angle
        jTis = self.jTi_list(q)

        for i, (link, jTi, v_j, twist_j, torque_j, kTj) \
                in enumerate(zip(self._links, jTis, joint_velocities, twists, torques, jTis[1:])):
            j = i + 1
            jRw = Ts[i].rotation().inverse()
            gravity_j = None if gravity is None else utils.rotate(jRw, gravity)
            factors = link.forward_factors(
                j, jTi, v_j, twist_j, torque_j, kTj, gravity_j)
            gfg.push_back(factors)

        # Add factor to enforce external wrench at tool
        gfg.add(Link.tool_factor(self.num_links, external_wrench))

        return gfg

    def inverse_factor_graph(self, q, joint_velocities, joint_accelerations,
                             gravity=None, base_twist_accel=ZERO6, external_wrench=ZERO6):
        """ Build factor graph for solving inverse dynamics.
            Keyword arguments:
                q (np.array, in rad) - joint angles
                joint velocities (np.array, in rad/s)
                joint_accelerations (np.array, in rad/s^2)
                gravity (np.array) -- if given, will create gravity forces
                base_twist_accel (np.array) -- optional acceleration for base
                external_wrench (np.array) -- optional external wrench
            Note: see Link.base_factor on use of base_twist_accel
            Returns Gaussian factor graph
        """
        N = self.num_links
        assert q.shape == (N,)
        assert joint_velocities.shape == (N,)
        assert joint_accelerations.shape == (N,)

        # configuration of COM link frames
        Ts = self.com_frames(q)

        # Calculate all twists
        twists = self.twists(Ts, joint_velocities)

        # Set up Gaussian Factor Graph
        gfg = gtsam.GaussianFactorGraph()

        # Add factor to enforce base acceleration equal to zero
        gfg.add(Link.base_factor(base_twist_accel))

        # configuration of link frame j-1 relative to link frame j for arbitrary joint angle
        jTis = self.jTi_list(q)

        for i, (link, jTi, v_j, twist_j, acceleration_j, kTj) \
                in enumerate(zip(self._links, jTis, joint_velocities, twists, joint_accelerations, jTis[1:])):
            j = i + 1
            jRw = Ts[i].rotation().inverse()
            gravity_j = None if gravity is None else utils.rotate(jRw, gravity)
            factors = link.inverse_factors(
                j, jTi, v_j, twist_j, acceleration_j, kTj, gravity_j)
            gfg.push_back(factors)

        # Add factor to enforce external wrench at tool
        gfg.add(Link.tool_factor(self.num_links, external_wrench))

        return gfg

    def extract_joint_accelerations(self, result):
        """Extract joint accelerations for all joints from VectorValues."""
        return [result.at(a(j)) for j in range(1, self.num_links + 1)]

    def extract_torques(self, result):
        """Extract torques for all joints from VectorValues."""
        return [result.at(t(j)) for j in range(1, self.num_links + 1)]

    def factor_graph_optimization(self, forward_factor_graph):
        """ Optimize factor graph for manipulator forward dynamics.
            Keyword arguments: 
                forward_factor_graph -- factor graph for forward dynamics.
            Returns VectorValues with all unknowns:
                - N+1 twist accelerations (base + links)
                - N+1 torques (links + tool)
                - N joint accelerations.
            Note: use extract_joint_accelerations to filter out jojt accelerations.
        """
        return forward_factor_graph.optimize()

    def forward_dynamics(self, *args, **kwargs):
        """ Calculate joint accelerations from manipulator state and torques.
            See forward_factor_graph for input arguments.
        """
        factor_graph = self.forward_factor_graph(*args, **kwargs)
        result = factor_graph.optimize()
        return self.extract_joint_accelerations(result)

    def inverse_dynamics(self, *args, **kwargs):
        """ Calculate joint torques from manipulator state and joint accelerations.
            See inverse_factor_graph for input arguments.
        """
        factor_graph = self.inverse_factor_graph(*args, **kwargs)
        result = factor_graph.optimize()
        return self.extract_torques(result)
