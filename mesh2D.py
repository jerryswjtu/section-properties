import numpy as np
import elementDefinitions

class triMesh:
    '''
    Contains elements within the triangular mesh and computes and stores section properties
    '''

    def __init__(self, genMesh, elementType):
        triElements = [] # list holding all element objects

        if elementType == 'tri3':
            for tri in genMesh['triangles']:
                x1 = genMesh['vertices'][tri[0]][0]
                y1 = genMesh['vertices'][tri[0]][1]
                x2 = genMesh['vertices'][tri[1]][0]
                y2 = genMesh['vertices'][tri[1]][1]
                x3 = genMesh['vertices'][tri[2]][0]
                y3 = genMesh['vertices'][tri[2]][1]
                vertices = np.array([[x1,y1], [x2,y2], [x3,y3]])
                triElements.append(elementDefinitions.tri3(vertices, tri)) # add triangle to element list
        else:
            print 'Element type not programmed'

        self.elements = triElements # store element list in triMesh object
        self.triangulation = genMesh # store the generated mesh
        self.noNodes = len((genMesh)['vertices']) # total number of nodes in mesh
        self.initialise(genMesh)

    def initialise(self, mesh):
        # initialise variables
        totalArea = totalQx = totalQy = totalIxx_g = totalIyy_g = totalIxy_g = 0
        torsionK = np.zeros((self.noNodes, self.noNodes))
        torsionF = np.transpose(np.zeros(self.noNodes))

        # loop through all elements
        for i, el in enumerate(self.elements):
            # calculate total area
            totalArea += el.area

            # calculate first moments of area about global axis
            totalQx += el.Qx
            totalQy += el.Qy

            # calculate second moments of area about global axis
            totalIxx_g += el.ixx
            totalIyy_g += el.iyy
            totalIxy_g += el.ixy

            # assemble stiffness matrix and load vector for warping constant
            indxs = np.ix_(el.nodes, el.nodes)
            torsionK[indxs] += el.torsionKe
            torsionF[el.nodes] += el.torsionFe

        # ----------------------------------------------------------------------
        # GLOBAL xy AXIS PROPERTIES:
        # ----------------------------------------------------------------------
        # assign total area
        self.area = totalArea

        # assign first moments of area
        self.Qx = totalQx
        self.Qy = totalQy

        # calculate centroids
        self.cx = totalQy / totalArea
        self.cy = totalQx / totalArea

        # assign global axis second moments of area
        self.ixx_g = totalIxx_g
        self.iyy_g = totalIyy_g
        self.ixy_g = totalIxy_g

        # ----------------------------------------------------------------------
        # CENTROIDAL xy AXIS PROPERTIES:
        # ----------------------------------------------------------------------
        # calculate second moments of area about the centroidal xy axis
        self.ixx_c = totalIxx_g - totalQx ** 2 / totalArea
        self.iyy_c = totalIyy_g - totalQy ** 2 / totalArea
        self.ixy_c = totalIxy_g - totalQx * totalQy / totalArea

        # calculate section modulii about the centroidal xy axis
        xmax = self.triangulation['vertices'][:, 0].max()
        xmin = self.triangulation['vertices'][:, 0].min()
        ymax = self.triangulation['vertices'][:, 1].max()
        ymin = self.triangulation['vertices'][:, 1].min()
        self.zxx_plus = self.ixx_c / (ymax - self.cy)
        self.zxx_minus = self.ixx_c / (self.cy - ymin)
        self.zyy_plus = self.iyy_c / (xmax - self.cx)
        self.zyy_minus = self.iyy_c / (self.cx - xmin)

        # calculate radii of gyration about centroidal xy axis
        self.rx_c = (self.ixx_c / totalArea) ** 0.5
        self.ry_c = (self.iyy_c / totalArea) ** 0.5

        # ----------------------------------------------------------------------
        # PRCINCIPAL AXIS PROPERTIES:
        # ----------------------------------------------------------------------
        # calculate prinicpal second moments of area about the centroidal xy axis
        delta = (((self.ixx_c - self.iyy_c) / 2) ** 2 + self.ixy_c ** 2) ** 0.5
        self.i1_c = (self.ixx_c + self.iyy_c) / 2 + delta
        self.i2_c = (self.ixx_c + self.iyy_c) / 2 - delta

        # calculate initial principal axis angle
        self.phi = np.arctan2(self.ixx_c - self.i1_c, self.ixy_c) * 180 / np.pi

        # calculate radii of gyration about centroidal principal axis
        self.r1_c = (self.i1_c / totalArea) ** 0.5
        self.r2_c = (self.i2_c / totalArea) ** 0.5

        # ----------------------------------------------------------------------
        # TORSION PROPERTIES:
        # ----------------------------------------------------------------------
        # calculate warping constant and torsion constant
        self.w = np.linalg.solve(torsionK, torsionF)
        self.J = self.ixx_g + self.iyy_g - self.w.dot(torsionK).dot(np.transpose(self.w))