import sectionproperties.pre.sections as sections
import sectionproperties.pre.pre as pre

points = [[0, 0], [5, 0], [5, 5], [0, 0], [0, 5], [0, 0], [5.0000001, 0]]
facets = [[0, 1], [1, 2], [2, 4], [4, 0], [3, 1], [5, 1], [0, 6]]
holes = []
control_points = [[2.5, 2.5]]

geometry = sections.CustomSection(points, facets, holes, control_points)
cleaner = pre.GeometryCleaner(geometry)
geometry = cleaner.clean_geometry()
geometry.plot_geometry()

print(geometry.points)
print(geometry.facets)
# geometry = cleaner.geometry
# geometry.plot_geometry()
# mesh = geometry.create_mesh(mesh_sizes=[5, 10])
#
# section = CrossSection(geometry, mesh)
# section.display_mesh_info()
# section.plot_mesh()
# section.calculate_geometric_properties(time_info=True)
# section.calculate_warping_properties(time_info=True)
# # section.calculate_plastic_properties()
# stress_result = section.calculate_stress(N=1e3, Vy=3e3, Mxx=1e6, Mzz=5e5,
#                                          time_info=True)
#
# section.plot_centroids()
# section.display_results()
# stress_result.plot_stress_n_zz()