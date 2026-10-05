from SGMG.geometry_storage import GeometryStorage, Sketch, Curve
import numpy as np
from helpers.bezier import bezierCurve


class splined2DGeometryInletHEXOutlet:
    def __init__(self, input_dict: dict = {}):
        # Input
        ## Diff duct coordinates
        hub_inlet = -20e-3
        shroud_inlet = 20e-3 # 4cm
        D_h_inlet = shroud_inlet - hub_inlet
        L_diffuser = input_dict["L_diffuser"]

        ## Diff duct area ruling, solves for missing coordinate
        if input_dict["AR"] is not None:
            AR = input_dict["AR"]            
        elif input_dict["wall_angle"] is not None:
            delta_D_h = 2 * L_diffuser * np.tan(np.deg2rad(input_dict["wall_angle"]))
            AR = (D_h_inlet + delta_D_h) / D_h_inlet
        else:
            pass

        D_h_outlet = D_h_inlet * AR
        hub_outlet = -D_h_outlet / 2
        shroud_outlet = D_h_outlet / 2
        
        ## Lengths and angles
        L_inlet = 115e-3
        L_hex = 24e-3
        L_contraction = 2 * D_h_inlet
        L_out = D_h_inlet
        # alpha = 0

        ## Spline tangents
        inlet_tangent_upper = np.array([1,0])
        inlet_tangent_lower = np.array([1,0])
        outlet_tangent_upper = np.array([-1,0])
        outlet_tangent_lower = np.array([-1,0])

        ## Control points for the bezier curves (https://www.desmos.com/calculator/cahqdxeshd)
        lambda1 = 0.1
        lambda2 = 0.1
        lambda3 = 0.1
        lambda4 = 0.1
        lambda5 = 0.15
        lambda6 = 0.15
        lambda7 = 0.25
        lambda8 = 0.25


        # Generation
        self.geometry = GeometryStorage("geometry")
        inlet_sketch = Sketch("inlet")
        hex_sketch = Sketch("hex")
        outlet_sketch = Sketch("outlet")

        p00 = np.array([-L_inlet, hub_inlet])
        p01 = np.array([-L_inlet, shroud_inlet])

        p10 = np.array([0, hub_inlet])
        p11 = np.array([0, shroud_inlet])

        # TODO: Rotate p2x and p3x alpha degrees
        p20 = np.array([L_diffuser, hub_outlet])
        p21 = np.array([L_diffuser, shroud_outlet])

        p30 = np.array([L_diffuser + L_hex, hub_outlet])
        p31 = np.array([L_diffuser + L_hex, shroud_outlet])

        # hex_midpoint = (p20 + p21 + p30 + p31)/4
        # p20 = rotate_point(p20, hex_midpoint, alpha)
        # p21 = rotate_point(p21, hex_midpoint, alpha)
        # p30 = rotate_point(p30, hex_midpoint, alpha)
        # p31 = rotate_point(p31, hex_midpoint, alpha)

        p40 = np.array([L_diffuser + L_hex + L_contraction, hub_outlet])
        p41 = np.array([L_diffuser + L_hex + L_contraction, shroud_outlet])

        p50 = np.array([L_diffuser + L_hex + L_contraction + L_out, hub_outlet])
        p51 = np.array([L_diffuser + L_hex + L_contraction + L_out, shroud_outlet])

        # Tangets for splines
        inlet_tangent_upper = inlet_tangent_upper / np.linalg.norm(inlet_tangent_upper) * np.linalg.norm(p21-p11) * lambda2
        inlet_tangent_lower = inlet_tangent_lower / np.linalg.norm(inlet_tangent_lower) * np.linalg.norm(p20-p10) * lambda1

        hex_inlet_tangent_upper = (p21 - p31) / np.linalg.norm(p31 - p21) * np.linalg.norm(p21-p11) * lambda4
        hex_inlet_tangent_lower = (p20 - p30) / np.linalg.norm(p30 - p20) * np.linalg.norm(p20-p10) * lambda3
        
        hex_outlet_tangent_upper = (p31 - p21) / np.linalg.norm(p31 - p21) * np.linalg.norm(p41-p31) * lambda6
        hex_outlet_tangent_lower = (p30 - p20) / np.linalg.norm(p30 - p20) * np.linalg.norm(p40-p30) * lambda5

        outlet_tangent_upper = outlet_tangent_upper / np.linalg.norm(outlet_tangent_upper) * np.linalg.norm(p41-p31) * lambda8
        outlet_tangent_lower = outlet_tangent_lower / np.linalg.norm(outlet_tangent_lower) * np.linalg.norm(p40-p30) * lambda7

        # Inlet and diffusing duct curves
        c001 = Curve(np.linspace(p00, p01, 2), "inlet")
        c000 = Curve(np.linspace(p00, p10, 2), "inlet_wall_lower")
        c010 = Curve(np.linspace(p01, p11, 2), "inlet_wall_upper")
        c100 = Curve(bezierCurve([p10, p10 + inlet_tangent_lower, p20 + hex_inlet_tangent_lower, p20], 250), "diff_wall_lower")
        c110 = Curve(bezierCurve([p11, p11 + inlet_tangent_upper, p21 + hex_inlet_tangent_upper, p21], 250), "diff_wall_upper")
        c201 = Curve(np.linspace(p20, p21, 2), "hex_inlet_interface")
        for curve in [c001, c000, c010, c100, c110, c201]:
            inlet_sketch.add_curve(curve)
        self.geometry.add_sketch(inlet_sketch)


        # HEX curves
        c200 = Curve(np.linspace(p20, p30, 2), "hex_wall_lower")
        c210 = Curve(np.linspace(p21, p31, 2), "hex_wall_upper")
        c301 = Curve(np.linspace(p30, p31, 2), "hex_outlet_interface")
        for curve in [c200, c210, c201, c301]:
            hex_sketch.add_curve(curve)
        self.geometry.add_sketch(hex_sketch)


        # Outlet curves
        c300 = Curve(bezierCurve([p30, p30 + hex_outlet_tangent_lower, p40 + outlet_tangent_lower, p40], 250), "cont_wall_lower")
        c310 = Curve(bezierCurve([p31, p31 + hex_outlet_tangent_upper, p41 + outlet_tangent_upper, p41], 250), "cont_wall_upper")
        c400 = Curve(np.linspace(p40, p50, 2), "outlet_wall_lower")
        c410 = Curve(np.linspace(p41, p51, 2), "outlet_wall_upper")
        c501 = Curve(np.linspace(p50, p51, 2), "outlet")
        for curve in [c301, c300, c310, c400, c410, c501]:
            outlet_sketch.add_curve(curve)
        self.geometry.add_sketch(outlet_sketch)

class straightwalled2DGeometryInletHEXOutlet:
    def __init__(self, input_dict: dict = {}):
        # Input
        ## Diff duct coordinates
        hub_inlet = -20e-3
        shroud_inlet = 20e-3 # 4cm
        D_h_inlet = shroud_inlet - hub_inlet
        L_diffuser = input_dict["L_diffuser"]

        ## Diff duct area ruling, solves for missing coordinate
        if input_dict["AR"] is not None:
            AR = input_dict["AR"]            
        elif input_dict["wall_angle"] is not None:
            delta_D_h = 2 * L_diffuser * np.tan(np.deg2rad(input_dict["wall_angle"]))
            AR = (D_h_inlet + delta_D_h) / D_h_inlet
        else:
            pass

        D_h_outlet = D_h_inlet * AR
        hub_outlet = -D_h_outlet / 2
        shroud_outlet = D_h_outlet / 2
        
        ## Lengths and angles
        L_inlet = 115e-3
        L_hex = 24e-3
        L_contraction = 2 * D_h_inlet
        L_out = D_h_inlet
        # alpha = 0


        # Generation
        self.geometry = GeometryStorage("geometry")
        inlet_sketch = Sketch("inlet")
        hex_sketch = Sketch("hex")
        outlet_sketch = Sketch("outlet")

        p00 = np.array([-L_inlet, hub_inlet])
        p01 = np.array([-L_inlet, shroud_inlet])

        p10 = np.array([0, hub_inlet])
        p11 = np.array([0, shroud_inlet])

        # TODO: Rotate p2x and p3x alpha degrees
        p20 = np.array([L_diffuser, hub_outlet])
        p21 = np.array([L_diffuser, shroud_outlet])

        p30 = np.array([L_diffuser + L_hex, hub_outlet])
        p31 = np.array([L_diffuser + L_hex, shroud_outlet])

        # hex_midpoint = (p20 + p21 + p30 + p31)/4
        # p20 = rotate_point(p20, hex_midpoint, alpha)
        # p21 = rotate_point(p21, hex_midpoint, alpha)
        # p30 = rotate_point(p30, hex_midpoint, alpha)
        # p31 = rotate_point(p31, hex_midpoint, alpha)

        p40 = np.array([L_diffuser + L_hex + L_contraction, hub_outlet])
        p41 = np.array([L_diffuser + L_hex + L_contraction, shroud_outlet])

        p50 = np.array([L_diffuser + L_hex + L_contraction + L_out, hub_outlet])
        p51 = np.array([L_diffuser + L_hex + L_contraction + L_out, shroud_outlet])

        # Inlet and diffusing duct curves
        c001 = Curve(np.linspace(p00, p01, 2), "inlet")
        c000 = Curve(np.linspace(p00, p10, 2), "inlet_wall_lower")
        c010 = Curve(np.linspace(p01, p11, 2), "inlet_wall_upper")
        c100 = Curve(np.linspace(p10, p20, 2), "diff_wall_lower")
        c110 = Curve(np.linspace(p11, p21, 2), "diff_wall_upper")
        c201 = Curve(np.linspace(p20, p21, 2), "hex_inlet_interface")
        for curve in [c001, c000, c010, c100, c110, c201]:
            inlet_sketch.add_curve(curve)
        self.geometry.add_sketch(inlet_sketch)


        # HEX curves
        c200 = Curve(np.linspace(p20, p30, 2), "hex_wall_lower")
        c210 = Curve(np.linspace(p21, p31, 2), "hex_wall_upper")
        c301 = Curve(np.linspace(p30, p31, 2), "hex_outlet_interface")
        for curve in [c200, c210, c201, c301]:
            hex_sketch.add_curve(curve)
        self.geometry.add_sketch(hex_sketch)


        # Outlet curves
        c300 = Curve(np.linspace(p30, p40, 2), "cont_wall_lower")
        c310 = Curve(np.linspace(p31, p41, 2), "cont_wall_upper")
        c400 = Curve(np.linspace(p40, p50, 2), "outlet_wall_lower")
        c410 = Curve(np.linspace(p41, p51, 2), "outlet_wall_upper")
        c501 = Curve(np.linspace(p50, p51, 2), "outlet")
        for curve in [c301, c300, c310, c400, c410, c501]:
            outlet_sketch.add_curve(curve)
        self.geometry.add_sketch(outlet_sketch)


class defined2DGeometryInletHEXOutlet:
    def __init__(self, lower_wall_pts, upper_wall_pts, input_dict = {}):
        # Input
        ## Diff duct coordinates
        hub_inlet = -20e-3
        shroud_inlet = 20e-3 # 4cm
        D_h_inlet = shroud_inlet - hub_inlet
        L_diffuser = input_dict["L_diffuser"]

        shroud_outlet = upper_wall_pts[-1][1]
        hub_outlet = lower_wall_pts[-1][1]
        ## Lengths and angles
        L_inlet = 115e-3
        L_hex = 24e-3
        L_contraction = 2 * D_h_inlet
        L_out = D_h_inlet
        # alpha = 0

        ## Spline tangents
        outlet_tangent_upper = np.array([-1,0])
        outlet_tangent_lower = np.array([-1,0])

        ## Control points for the bezier curves (https://www.desmos.com/calculator/cahqdxeshd)
        lambda5 = 0.15
        lambda6 = 0.15
        lambda7 = 0.25
        lambda8 = 0.25


        # Generation
        self.geometry = GeometryStorage("geometry")
        inlet_sketch = Sketch("inlet")
        hex_sketch = Sketch("hex")
        outlet_sketch = Sketch("outlet")

        p00 = np.array([-L_inlet, hub_inlet])
        p01 = np.array([-L_inlet, shroud_inlet])

        p10 = np.array([0, hub_inlet])
        p11 = np.array([0, shroud_inlet])

        # TODO: Rotate p2x and p3x alpha degrees
        p20 = np.array([L_diffuser, hub_outlet])
        p21 = np.array([L_diffuser, shroud_outlet])

        p30 = np.array([L_diffuser + L_hex, hub_outlet])
        p31 = np.array([L_diffuser + L_hex, shroud_outlet])

        # hex_midpoint = (p20 + p21 + p30 + p31)/4
        # p20 = rotate_point(p20, hex_midpoint, alpha)
        # p21 = rotate_point(p21, hex_midpoint, alpha)
        # p30 = rotate_point(p30, hex_midpoint, alpha)
        # p31 = rotate_point(p31, hex_midpoint, alpha)

        p40 = np.array([L_diffuser + L_hex + L_contraction, hub_outlet])
        p41 = np.array([L_diffuser + L_hex + L_contraction, shroud_outlet])

        p50 = np.array([L_diffuser + L_hex + L_contraction + L_out, hub_outlet])
        p51 = np.array([L_diffuser + L_hex + L_contraction + L_out, shroud_outlet])


        # Inlet and diffusing duct curves
        c001 = Curve(np.linspace(p00, p01, 2), "inlet")
        c000 = Curve(np.linspace(p00, p10, 2), "inlet_wall_lower")
        c010 = Curve(np.linspace(p01, p11, 2), "inlet_wall_upper")
        c100 = Curve(lower_wall_pts, "diff_wall_lower")
        c110 = Curve(upper_wall_pts, "diff_wall_upper")
        c201 = Curve(np.linspace(p20, p21, 2), "hex_inlet_interface")
        for curve in [c001, c000, c010, c100, c110, c201]:
            inlet_sketch.add_curve(curve)
        self.geometry.add_sketch(inlet_sketch)


        # HEX curves
        c200 = Curve(np.linspace(p20, p30, 2), "hex_wall_lower")
        c210 = Curve(np.linspace(p21, p31, 2), "hex_wall_upper")
        c301 = Curve(np.linspace(p30, p31, 2), "hex_outlet_interface")
        for curve in [c200, c210, c201, c301]:
            hex_sketch.add_curve(curve)
        self.geometry.add_sketch(hex_sketch)


        # Outlet curves
        c300 = Curve(np.linspace(p30, p40, 2), "cont_wall_lower")
        c310 = Curve(np.linspace(p31, p41, 2), "cont_wall_upper")
        c400 = Curve(np.linspace(p40, p50, 2), "outlet_wall_lower")
        c410 = Curve(np.linspace(p41, p51, 2), "outlet_wall_upper")
        c501 = Curve(np.linspace(p50, p51, 2), "outlet")
        for curve in [c301, c300, c310, c400, c410, c501]:
            outlet_sketch.add_curve(curve)
        self.geometry.add_sketch(outlet_sketch)

class defined2DGeometryInletHEXVariableContractionOutlet:
    def __init__(self, lower_wall_pts, upper_wall_pts, input_dict: dict = {}):
        # Input
        ## Diff duct coordinates
        hub_inlet = -20e-3
        shroud_inlet = 20e-3 # 4cm
        D_h_inlet = shroud_inlet - hub_inlet
        L_diffuser = input_dict["L_diffuser"]
 
        shroud_outlet = upper_wall_pts[-1][1]
        hub_outlet = lower_wall_pts[-1][1]
 
        ## Fixed outlet: 2x inlet area, centred on the axis
        D_h_hex = shroud_outlet - hub_outlet
        D_h_exit = min(D_h_hex, 2 * D_h_inlet)
        y_mid_hex = (shroud_outlet + hub_outlet) / 2
        hub_exit = y_mid_hex - D_h_exit / 2
        shroud_exit = y_mid_hex + D_h_exit / 2
 
        ## Lengths and angles
        L_inlet = 115e-3
        L_hex = 24e-3
        L_contraction = 2 * D_h_inlet
        L_out = D_h_inlet
        # alpha = 0
 
        ## Spline tangents
        outlet_tangent_upper = np.array([-1,0])
        outlet_tangent_lower = np.array([-1,0])
 
        ## Control points for the bezier curves (https://www.desmos.com/calculator/cahqdxeshd)
        lambda5 = 0.30
        lambda6 = 0.30
        lambda7 = 0.30
        lambda8 = 0.30
 
 
        # Generation
        self.geometry = GeometryStorage("geometry")
        inlet_sketch = Sketch("inlet")
        hex_sketch = Sketch("hex")
        outlet_sketch = Sketch("outlet")
 
        p00 = np.array([-L_inlet, hub_inlet])
        p01 = np.array([-L_inlet, shroud_inlet])
 
        p10 = np.array([0, hub_inlet])
        p11 = np.array([0, shroud_inlet])
 
        # TODO: Rotate p2x and p3x alpha degrees
        p20 = np.array([L_diffuser, hub_outlet])
        p21 = np.array([L_diffuser, shroud_outlet])
 
        p30 = np.array([L_diffuser + L_hex, hub_outlet])
        p31 = np.array([L_diffuser + L_hex, shroud_outlet])
 
        # hex_midpoint = (p20 + p21 + p30 + p31)/4
        # p20 = rotate_point(p20, hex_midpoint, alpha)
        # p21 = rotate_point(p21, hex_midpoint, alpha)
        # p30 = rotate_point(p30, hex_midpoint, alpha)
        # p31 = rotate_point(p31, hex_midpoint, alpha)
 
        p40 = np.array([L_diffuser + L_hex + L_contraction, hub_exit])
        p41 = np.array([L_diffuser + L_hex + L_contraction, shroud_exit])
 
        p50 = np.array([L_diffuser + L_hex + L_contraction + L_out, hub_exit])
        p51 = np.array([L_diffuser + L_hex + L_contraction + L_out, shroud_exit])
 
        # Tangents for splines
        hex_outlet_tangent_upper = (p31 - p21) / np.linalg.norm(p31 - p21) * np.linalg.norm(p41-p31) * lambda6
        hex_outlet_tangent_lower = (p30 - p20) / np.linalg.norm(p30 - p20) * np.linalg.norm(p40-p30) * lambda5
 
        outlet_tangent_upper = outlet_tangent_upper / np.linalg.norm(outlet_tangent_upper) * np.linalg.norm(p41-p31) * lambda8
        outlet_tangent_lower = outlet_tangent_lower / np.linalg.norm(outlet_tangent_lower) * np.linalg.norm(p40-p30) * lambda7
 
 
        # Inlet and diffusing duct curves
        c001 = Curve(np.linspace(p00, p01, 2), "inlet")
        c000 = Curve(np.linspace(p00, p10, 2), "inlet_wall_lower")
        c010 = Curve(np.linspace(p01, p11, 2), "inlet_wall_upper")
        c100 = Curve(lower_wall_pts, "diff_wall_lower")
        c110 = Curve(upper_wall_pts, "diff_wall_upper")
        c201 = Curve(np.linspace(p20, p21, 2), "hex_inlet_interface")
        for curve in [c001, c000, c010, c100, c110, c201]:
            inlet_sketch.add_curve(curve)
        self.geometry.add_sketch(inlet_sketch)
 
 
        # HEX curves
        c200 = Curve(np.linspace(p20, p30, 2), "hex_wall_lower")
        c210 = Curve(np.linspace(p21, p31, 2), "hex_wall_upper")
        c301 = Curve(np.linspace(p30, p31, 2), "hex_outlet_interface")
        for curve in [c200, c210, c201, c301]:
            hex_sketch.add_curve(curve)
        self.geometry.add_sketch(hex_sketch)
 
 
        # Outlet curves
        c300 = Curve(bezierCurve([p30, p30 + hex_outlet_tangent_lower, p40 + outlet_tangent_lower, p40], 250), "cont_wall_lower")
        c310 = Curve(bezierCurve([p31, p31 + hex_outlet_tangent_upper, p41 + outlet_tangent_upper, p41], 250), "cont_wall_upper")
        c400 = Curve(np.linspace(p40, p50, 2), "outlet_wall_lower")
        c410 = Curve(np.linspace(p41, p51, 2), "outlet_wall_upper")
        c501 = Curve(np.linspace(p50, p51, 2), "outlet")
        for curve in [c301, c300, c310, c400, c410, c501]:
            outlet_sketch.add_curve(curve)
        self.geometry.add_sketch(outlet_sketch)

from helpers.geometry_helpers import filletedStraightWall
class straightwalledWithRadii2DGeometryInletHEXOutlet:
    def __init__(self, input_dict: dict = {}):
        # Input
        ## Diff duct coordinates
        hub_inlet = -20e-3
        shroud_inlet = 20e-3 # 4cm
        D_h_inlet = shroud_inlet - hub_inlet
        L_diffuser = input_dict["L_diffuser"]
 
        ## Diff duct area ruling, solves for missing coordinate
        if input_dict["AR"] is not None:
            AR = input_dict["AR"]            
        elif input_dict["wall_angle"] is not None:
            delta_D_h = 2 * L_diffuser * np.tan(np.deg2rad(input_dict["wall_angle"]))
            AR = (D_h_inlet + delta_D_h) / D_h_inlet
        else:
            pass
 
        D_h_outlet = D_h_inlet * AR
        hub_outlet = -D_h_outlet / 2
        shroud_outlet = D_h_outlet / 2
        
        ## Lengths and angles
        L_inlet = 115e-3
        L_hex = 24e-3
        L_contraction = 2 * D_h_inlet
        L_out = D_h_inlet
        # alpha = 0
 
        ## Corner fillets: fixed radius relative to inlet height, same at both corners
        ## and for every geometry. Set to 0 for sharp corners.
        R_over_W = input_dict.get("fillet_R_over_W", 1.0)
        R_fillet = R_over_W * D_h_inlet
 
 
        # Generation
        self.geometry = GeometryStorage("geometry")
        inlet_sketch = Sketch("inlet")
        hex_sketch = Sketch("hex")
        outlet_sketch = Sketch("outlet")
 
        p00 = np.array([-L_inlet, hub_inlet])
        p01 = np.array([-L_inlet, shroud_inlet])
 
        p10 = np.array([0, hub_inlet])
        p11 = np.array([0, shroud_inlet])
 
        # TODO: Rotate p2x and p3x alpha degrees
        p20 = np.array([L_diffuser, hub_outlet])
        p21 = np.array([L_diffuser, shroud_outlet])
 
        p30 = np.array([L_diffuser + L_hex, hub_outlet])
        p31 = np.array([L_diffuser + L_hex, shroud_outlet])
 
        # hex_midpoint = (p20 + p21 + p30 + p31)/4
        # p20 = rotate_point(p20, hex_midpoint, alpha)
        # p21 = rotate_point(p21, hex_midpoint, alpha)
        # p30 = rotate_point(p30, hex_midpoint, alpha)
        # p31 = rotate_point(p31, hex_midpoint, alpha)
 
        p40 = np.array([L_diffuser + L_hex + L_contraction, hub_outlet])
        p41 = np.array([L_diffuser + L_hex + L_contraction, shroud_outlet])
 
        p50 = np.array([L_diffuser + L_hex + L_contraction + L_out, hub_outlet])
        p51 = np.array([L_diffuser + L_hex + L_contraction + L_out, shroud_outlet])
 
        # Inlet and diffusing duct curves
        c001 = Curve(np.linspace(p00, p01, 2), "inlet")
        c000 = Curve(np.linspace(p00, p10, 2), "inlet_wall_lower")
        c010 = Curve(np.linspace(p01, p11, 2), "inlet_wall_upper")
        lower_pts, lower_info = filletedStraightWall(hub_inlet, hub_outlet, L_diffuser, R_fillet)
        upper_pts, upper_info = filletedStraightWall(shroud_inlet, shroud_outlet, L_diffuser, R_fillet)
        self.fillet_info = {"R": R_fillet, "R_over_W": R_over_W,
                            "lower": lower_info, "upper": upper_info}
        c100 = Curve(lower_pts, "diff_wall_lower")
        c110 = Curve(upper_pts, "diff_wall_upper")
        c201 = Curve(np.linspace(p20, p21, 2), "hex_inlet_interface")
        for curve in [c001, c000, c010, c100, c110, c201]:
            inlet_sketch.add_curve(curve)
        self.geometry.add_sketch(inlet_sketch)
 
 
        # HEX curves
        c200 = Curve(np.linspace(p20, p30, 2), "hex_wall_lower")
        c210 = Curve(np.linspace(p21, p31, 2), "hex_wall_upper")
        c301 = Curve(np.linspace(p30, p31, 2), "hex_outlet_interface")
        for curve in [c200, c210, c201, c301]:
            hex_sketch.add_curve(curve)
        self.geometry.add_sketch(hex_sketch)
 
 
        # Outlet curves
        c300 = Curve(np.linspace(p30, p40, 2), "cont_wall_lower")
        c310 = Curve(np.linspace(p31, p41, 2), "cont_wall_upper")
        c400 = Curve(np.linspace(p40, p50, 2), "outlet_wall_lower")
        c410 = Curve(np.linspace(p41, p51, 2), "outlet_wall_upper")
        c501 = Curve(np.linspace(p50, p51, 2), "outlet")
        for curve in [c301, c300, c310, c400, c410, c501]:
            outlet_sketch.add_curve(curve)
        self.geometry.add_sketch(outlet_sketch)
