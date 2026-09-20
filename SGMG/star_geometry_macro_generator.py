import numpy as np
from pathlib import Path
from io import TextIOWrapper

from SGMG.geometry_storage import GeometryStorage, Sketch, Curve
from SGMG.generate_macro_bindings import macro_bindings


class StarGeometryMacroGenerator:
    def __init__(
        self, geometry: GeometryStorage, fileName: str, path=Path.cwd()
    ) -> Path:
        if fileName[-5:] != ".java":
            fileName += ".java"
        self.filePath = path / fileName
        self.sketches = {}

        with open(self.filePath, "w+") as macroFile:


            sketches = list(geometry.get_sketches().values())

            # Split sketches
            unite_sketches = [s for s in sketches if s.unite]
            unite_sketches.sort(key=lambda s: s.name)
            normal_sketches = [s for s in sketches if not s.unite]

            num_sketches = 1 if unite_sketches else 0
            macro_bindings.write_entry(
                macroFile, fileName, len(geometry.get_sketches()) + num_sketches
            )
            macroFile.write("\n")

            index = 0

            # Sketch unite sketches, if they exist
            if len(unite_sketches):
                for sketch in unite_sketches:
                    self.__add_sketch(sketch, macroFile, index)
                    index += 1
                # Unite the sketches
                self.__unite_sketches(unite_sketches, macroFile, index)
                index += 1

            # Second loop: sketch the remaining sketches
            if len(normal_sketches):
                for sketch in normal_sketches:
                    self.__add_sketch(sketch, macroFile, index)
                    index += 1

            macro_bindings.write_end(
                macroFile, len(geometry.get_sketches()) + num_sketches, geometry.name
            )

    def getPath(self):
        return self.filePath

    def __add_sketch(self, sketch: Sketch, macroFile: TextIOWrapper, sketchNumber: int):
        if sketch.name in self.sketches:
            print("ERROR: sketch already exists")

        self.sketches[sketch.name] = {"anchors": [], "curves": [""] * sketch.length()}

        macro_bindings.write_sketch_start(macroFile, sketchNumber, sketch.name)
        macroFile.write("\n")

        # -------------------------------------------------
        # Write exactly ONE anchor point per curve
        # -------------------------------------------------
        for i, curveData in enumerate(sketch.curves):
            p0 = curveData.points[0]
            macroFile.write(
                f" PointSketchPrimitive {sketch.name}Point{i} = "
                f"{sketch.name}.createPoint(new DoubleVector(new double[] "
                f"{{{p0[0]:.6e}, {p0[1]:.6e}}}));\n"
            )
            self.sketches[sketch.name]["anchors"].append(f"{sketch.name}Point{i}")

        macroFile.write("\n")

        # -------------------------------------------------
        # Write exactly ONE spline per curve
        # -------------------------------------------------
        for i, curveData in enumerate(sketch.curves):
            pts = curveData.points
            if len(pts) < 2:
                continue

            coords = []
            for p in pts[1:]:
                coords.extend([p[0], p[1]])

            splineName = f"{sketch.name}Spline{i}"

            macroFile.write(
                f" SplineSketchPrimitive {splineName} = "
                f"{sketch.name}.createSpline(true, {sketch.name}Point{i}, "
                f"false, null, new DoubleVector(new double[] "
                f"{{{', '.join(f'{c:.6e}' for c in coords)}}}));\n"
            )

            self.sketches[sketch.name]["curves"][i] = {
                "faceName": curveData.face_name,
                "lines": [splineName],
            }

        macroFile.write("\n")

        # -------------------------------------------------
        # End sketching
        # -------------------------------------------------
        macro_bindings.end_sketching(macroFile, sketch.name)
        macroFile.write("\n")

        # -------------------------------------------------
        # Extrude or cut
        # -------------------------------------------------
        if sketch.type == "extrude":
            featureName = f"extrusionMerge_{sketch.name}"
            macro_bindings.write_extrude_sketch(macroFile, sketch.name, featureName)
        elif sketch.type == "cut":
            featureName = f"extrusionCut_{sketch.name}"
            macro_bindings.write_cut_sketch(macroFile, sketch.name, featureName)
        else:
            raise ValueError(f"Unknown sketch.type={sketch.type!r}")

        macroFile.write("\n")

        # -------------------------------------------------
        # Pick one spline for face access
        # -------------------------------------------------
        random_edge = None
        for c in self.sketches[sketch.name]["curves"]:
            if c["lines"]:
                random_edge = c["lines"][0]
                break

        if random_edge is None:
            print(f"WARNING: Sketch {sketch.name} produced no splines; skipping naming.")
            macroFile.write(" }\n\n")
            return

        # -------------------------------------------------
        # Name body (extrude only)
        # -------------------------------------------------
        if sketch.type == "extrude":
            cadbodyName = f"cadbody_{sketch.name}"
            macroFile.write(
                f" star.cadmodeler.Body {cadbodyName} = "
                f"((star.cadmodeler.Body) {featureName}.getBody({random_edge}));\n"
            )
            macroFile.write(f' {cadbodyName}.setPresentationName("{sketch.name}");\n\n')

        # -------------------------------------------------
        # Name end caps
        # -------------------------------------------------
        macroFile.write(
            f" Face face_0 = ((Face) {featureName}.getEndCapFace({random_edge}));"
        )
        macroFile.write(
            ' cadModel_0.setFaceNameAttributes(new ArrayList<>(Arrays.<Face>asList(face_0)), "2dsurf2", false);\n'
        )

        macroFile.write(
            f" Face face_1 = ((Face) {featureName}.getStartCapFace({random_edge}));"
        )
        macroFile.write(
            ' cadModel_0.setFaceNameAttributes(new ArrayList<>(Arrays.<Face>asList(face_1)), "2dsurf1", false);\n'
        )

        # -------------------------------------------------
        # Name side faces (one spline per face)
        # -------------------------------------------------
        sidefaces = {}
        for c in self.sketches[sketch.name]["curves"]:
            fname = c["faceName"]
            sidefaces.setdefault(fname, [])
            spline = c["lines"][0]
            faceVar = f"face_{spline}"
            macroFile.write(
                f' Face {faceVar} = ((Face) {featureName}.getSideFace({spline},"True"));\n'
            )
            sidefaces[fname].append(faceVar)

        macroFile.write("\n")

        for fname, faces in sidefaces.items():
            macroFile.write(
                f' cadModel_0.setFaceNameAttributes(new ArrayList<>(Arrays.<Face>asList({", ".join(faces)})), "{fname}", false);\n'
            )

        macroFile.write(" }\n\n")

    def __unite_sketches(
        self,
        sketches: list[Sketch],
        macroFile: TextIOWrapper,
        sketchNumber: int,
    ):
        if not sketches:
            return

        exec_num = sketchNumber + 1  # keep same convention as your other execute blocks

        # Header + locals
        macro_bindings.write_execute_start(macroFile, exec_num)

        # Unite block (mostly static lives in bindings)
        unite_feature_name = f"uniteBodiesFeature_{exec_num}"
        body_names = [s.name for s in sketches]  # assumes bodies are named by sketch.name
        macro_bindings.write_unite_bodies(macroFile, unite_feature_name, body_names)

        # Footer
        macro_bindings.write_execute_end(macroFile)

