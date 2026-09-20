from io import TextIOWrapper

MODEL_TMP_NAME = "SGMG_TMP_MODEL"


class macro_bindings:
    def __init__(self):
        pass

    def write_entry(macroFile: TextIOWrapper, fileName, numberOfSketches):
        macroFile.write(f"// Simcenter STAR-CCM+ macro: {fileName}\n")
        macroFile.write(f"// Written by Erik Hasselwander\n")
        macroFile.write(f"\n")
        macroFile.write(f"package macro;\n")
        macroFile.write(f"import java.util.*;\n")
        macroFile.write(f"import star.common.*;\n")
        macroFile.write(f"import star.base.neo.*;\n")
        macroFile.write(f"import star.cadmodeler.*;\n")
        macroFile.write(f"\n")
        macroFile.write(f"public class {fileName[:-5]} extends StarMacro {{\n")
        macroFile.write(f"\n")
        macroFile.write(f"  public void execute() {{\n")
        for i in range(numberOfSketches + 2):
            macroFile.write(f"    execute{i}();\n")
        macroFile.write(f"  }}\n")
        macroFile.write(f"\n")
        macroFile.write(f"  private void execute{0}() {{\n")
        macroFile.write(f"    Simulation simulation_0 = getActiveSimulation();\n")
        macroFile.write(
            f"    CadModel cadModel_0 = simulation_0.get(SolidModelManager.class).createSolidModel();\n\n"
        )
        macroFile.write(f"    cadModel_0.resetSystemOptions();\n")
        macroFile.write(f'    cadModel_0.setPresentationName("{MODEL_TMP_NAME}");\n')
        macroFile.write(f"  }}\n")

    def write_sketch_start(
        macroFile: TextIOWrapper, sketchNumber: int, sketchName: str
    ):
        macroFile.write(f"  private void execute{sketchNumber+1}() {{\n")
        macroFile.write(f"    Simulation simulation_0 = getActiveSimulation();\n")
        macroFile.write(
            f'    CadModel cadModel_0 = ((CadModel) simulation_0.get(SolidModelManager.class).getObject("{MODEL_TMP_NAME}"));\n\n'
        )
        macroFile.write(f"    cadModel_0.resetSystemOptions();\n")
        macroFile.write(
            f'    CanonicalSketchPlane canonicalSketchPlane_0 = ((CanonicalSketchPlane) cadModel_0.getFeature("XY"));\n'
        )
        macroFile.write(
            f"    Units units_0 = simulation_0.getUnitsManager().getPreferredUnits(Dimensions.Builder().length(1).build());\n"
        )
        macroFile.write(
            f'    Units units_1 = ((Units) simulation_0.getUnitsManager().getObject("deg"));\n'
        )
        macroFile.write(
            f"    LabCoordinateSystem labCoordinateSystem_0 = simulation_0.getCoordinateSystemManager().getLabCoordinateSystem();\n"
        )
        macroFile.write(
            f"    Sketch {sketchName} = cadModel_0.getFeatureManager().createSketch(canonicalSketchPlane_0);\n"
        )
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(false);\n")
        macroFile.write(
            f"    cadModel_0.getFeatureManager().startSketchEdit({sketchName});\n"
        )

    def end_sketching(macroFile: TextIOWrapper, sketchName):
        macroFile.write(f"    {sketchName}.setIsUptoDate(true);\n")
        macroFile.write(f"    {sketchName}.markFeatureForEdit();\n")
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(true);\n")
        macroFile.write(
            f"    cadModel_0.getFeatureManager().stopSketchEdit({sketchName}, true);\n"
        )
        macroFile.write(
            f"    cadModel_0.getFeatureManager().updateModelAfterFeatureEdited({sketchName}, null);\n"
        )

    def write_extrude_sketch(
        macroFile: TextIOWrapper, sketchName: str, extrusionName: str, height=0.1
    ):
        macroFile.write(
            f"    ExtrusionMerge {extrusionName} = cadModel_0.getFeatureManager().createExtrusionMerge({sketchName});\n"
        )
        macroFile.write(f"    {extrusionName}.setAutoPreview(true);\n")
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(false);\n")
        macroFile.write(f"    {extrusionName}.setDirectionOption(0);\n")
        macroFile.write(f"    {extrusionName}.setExtrudedBodyTypeOption(0);\n")
        macroFile.write(
            f"    {extrusionName}.getDistance().setValueAndUnits(0.1, units_0);\n"
        )
        macroFile.write(
            f"    {extrusionName}.getDistanceAsymmetric().setValueAndUnits(0.1, units_0);\n"
        )
        macroFile.write(
            f"    {extrusionName}.getOffsetDistance().setValueAndUnits(0.1, units_0);\n"
        )
        macroFile.write(f"    {extrusionName}.setDistanceOption(0);\n")
        macroFile.write(f"    {extrusionName}.setCoordinateSystemOption(0);\n")
        macroFile.write(
            f"    {extrusionName}.getDraftAngle().setValueAndUnits(10.0, units_1);\n"
        )
        macroFile.write(f"    {extrusionName}.setDraftOption(0);\n")
        macroFile.write(
            f"    {extrusionName}.setImportedCoordinateSystem(labCoordinateSystem_0);\n"
        )
        macroFile.write(
            f"    {extrusionName}.getDirectionAxis().setCoordinateSystem(labCoordinateSystem_0);\n"
        )
        macroFile.write(f"    {extrusionName}.getDirectionAxis().setUnits0(units_0);\n")
        macroFile.write(f"    {extrusionName}.getDirectionAxis().setUnits1(units_0);\n")
        macroFile.write(f"    {extrusionName}.getDirectionAxis().setUnits2(units_0);\n")
        macroFile.write(f'    {extrusionName}.getDirectionAxis().setDefinition("");\n')
        macroFile.write(
            f"    {extrusionName}.getDirectionAxis().setValue(new DoubleVector(new double[] {{0.0, 0.0, 1.0}}));\n"
        )
        macroFile.write(f"    {extrusionName}.setFace(null);\n")
        macroFile.write(f"    {extrusionName}.setBody(null);\n")
        macroFile.write(f"    {extrusionName}.setPlane(null);\n")
        macroFile.write(f"    {extrusionName}.setFeatureInputType(0);\n")
        macroFile.write(
            f"    {extrusionName}.setInputFeatureEdges(new ArrayList<>(Collections.<Edge>emptyList()));\n"
        )
        macroFile.write(f"    {extrusionName}.setSketch({sketchName});\n")
        macroFile.write(
            f"    {extrusionName}.setInteractingBodies(new ArrayList<>(Collections.<Body>emptyList()));\n"
        )
        macroFile.write(
            f"    {extrusionName}.setInteractingBodiesBodyGroups(new ArrayList<>(Collections.<BodyGroup>emptyList()));\n"
        )
        macroFile.write(
            f"    {extrusionName}.setInteractingBodiesCadFilters(new ArrayList<>(Collections.<CadFilter>emptyList()));\n"
        )
        macroFile.write(f"    {extrusionName}.setInteractingSelectedBodies(false);\n")
        macroFile.write(f"    {extrusionName}.setPostOption(0);\n")
        macroFile.write(f"    {extrusionName}.setExtrusionOption(0);\n")
        macroFile.write(f"    {extrusionName}.setIsBodyGroupCreation(false);\n")
        macroFile.write(
            f"    cadModel_0.getFeatureManager().markDependentNotUptodate({extrusionName});\n"
        )
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(true);\n")
        macroFile.write(f"    {extrusionName}.markFeatureForEdit();\n")
        macroFile.write(
            f"    cadModel_0.getFeatureManager().execute({extrusionName});\n"
        )

    def write_end(macroFile: TextIOWrapper, numberOfSketches, modelName):
        macroFile.write(f"  private void execute{numberOfSketches+1}() {{\n")
        macroFile.write(f"    Simulation simulation_0 = getActiveSimulation();\n")
        macroFile.write(
            f'    CadModel cadModel_0 = ((CadModel) simulation_0.get(SolidModelManager.class).getObject("{MODEL_TMP_NAME}"));\n\n'
        )
        macroFile.write(f"    cadModel_0.resetSystemOptions();\n")
        macroFile.write(f'    cadModel_0.setPresentationName("{modelName}");\n')
        macroFile.write(f"  }}\n")
        macroFile.write(f"}}\n")

    def write_cut_sketch(
        macroFile: TextIOWrapper, sketchName: str, cutName: str, depth=0.1
    ):
        macroFile.write(
            f"    ExtrusionCut {cutName} = cadModel_0.getFeatureManager().createExtrusionCut({sketchName});\n"
        )
        macroFile.write(f"    {cutName}.setAutoPreview(true);\n")
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(false);\n")
        macroFile.write(f"    {cutName}.setDirectionOption(0);\n")
        macroFile.write(f"    {cutName}.setExtrudedBodyTypeOption(0);\n")
        macroFile.write(f"    {cutName}.getDistance().setValueAndUnits({depth}, units_0);\n")
        macroFile.write(f"    {cutName}.getDistanceAsymmetric().setValueAndUnits({depth}, units_0);\n")
        macroFile.write(f"    {cutName}.getOffsetDistance().setValueAndUnits({depth}, units_0);\n")
        macroFile.write(f"    {cutName}.setDistanceOption(0);\n")
        macroFile.write(f"    {cutName}.setCoordinateSystemOption(0);\n")
        macroFile.write(f"    {cutName}.getDraftAngle().setValueAndUnits(10.0, units_1);\n")
        macroFile.write(f"    {cutName}.setDraftOption(0);\n")
        macroFile.write(f"    {cutName}.setImportedCoordinateSystem(labCoordinateSystem_0);\n")
        macroFile.write(f"    {cutName}.getDirectionAxis().setCoordinateSystem(labCoordinateSystem_0);\n")
        macroFile.write(f"    {cutName}.getDirectionAxis().setUnits0(units_0);\n")
        macroFile.write(f"    {cutName}.getDirectionAxis().setUnits1(units_0);\n")
        macroFile.write(f"    {cutName}.getDirectionAxis().setUnits2(units_0);\n")
        macroFile.write(f'    {cutName}.getDirectionAxis().setDefinition("");\n')
        macroFile.write(
            f"    {cutName}.getDirectionAxis().setValue(new DoubleVector(new double[] {{0.0, 0.0, 1.0}}));\n"
        )
        macroFile.write(f"    {cutName}.setFace(null);\n")
        macroFile.write(f"    {cutName}.setBody(null);\n")
        macroFile.write(f"    {cutName}.setPlane(null);\n")
        macroFile.write(f"    {cutName}.setFeatureInputType(0);\n")
        macroFile.write(
            f"    {cutName}.setInputFeatureEdges(new ArrayList<>(Collections.<Edge>emptyList()));\n"
        )
        macroFile.write(f"    {cutName}.setSketch({sketchName});\n")

        # Cut-specific bits (from recorded macro)
        macroFile.write(f"    {cutName}.setExtrusionOption(1);\n")
        macroFile.write(f"    {cutName}.setSubtractingSelectedCutBodies(false);\n")
        macroFile.write(
            f"    {cutName}.setCutBodiesCadFilters(new ArrayList<>(Collections.<CadFilter>emptyList()));\n"
        )
        macroFile.write(
            f"    {cutName}.setCutBodies(new ArrayList<>(Collections.<Body>emptyList()));\n"
        )
        macroFile.write(
            f"    {cutName}.setCutBodiesBodyGroups(new ArrayList<>(Collections.<BodyGroup>emptyList()));\n"
        )
        macroFile.write(f"    {cutName}.setApplyToAllInstances(false);\n")
        macroFile.write(
            f"    {cutName}.setExcludedInstancedBodies(new ArrayList<>(Collections.<Body>emptyList()));\n"
        )
        macroFile.write(f"    {cutName}.setIsBodyGroupCreation(false);\n")
        macroFile.write(
            f"    cadModel_0.getFeatureManager().markDependentNotUptodate({cutName});\n"
        )
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(true);\n")
        macroFile.write(f"    {cutName}.markFeatureForEdit();\n")
        macroFile.write(f"    cadModel_0.getFeatureManager().execute({cutName});\n")

    def write_execute_start(macroFile: TextIOWrapper, execNumber: int):
        macroFile.write(f"  private void execute{execNumber}() {{\n")
        macroFile.write(f"    Simulation simulation_0 = getActiveSimulation();\n")
        macroFile.write(
            f'    CadModel cadModel_0 = ((CadModel) simulation_0.get(SolidModelManager.class).getObject("{MODEL_TMP_NAME}"));\n\n'
        )

    def write_execute_end(macroFile: TextIOWrapper):
        macroFile.write("  }\n\n")


    def write_unite_bodies(
        macroFile: TextIOWrapper,
        uniteFeatureName: str,
        bodyPresentationNames: list[str],
    ):
        """
        Writes a UniteBodiesFeature block. Assumes variables `simulation_0` and `cadModel_0`
        exist in the current execute method (provided by write_execute_start).
        """
        macroFile.write(
            f"    UniteBodiesFeature {uniteFeatureName} = cadModel_0.getFeatureManager().createUniteBodies2();\n\n"
        )

        macroFile.write(f"    {uniteFeatureName}.setKeepImprintedEdges(false);\n\n")
        macroFile.write(f"    {uniteFeatureName}.setAutoPreview(true);\n\n")
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(false);\n\n")

        # STAR macro often repeats these; harmless and matches recorded macro style.
        macroFile.write(f"    {uniteFeatureName}.setAutoPreview(true);\n\n")
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(false);\n\n")

        macroFile.write(f"    {uniteFeatureName}.setImprintOption(0);\n\n")

        macroFile.write('    Units units_0 = ((Units) simulation_0.getUnitsManager().getObject("m"));\n\n')
        macroFile.write(f"    {uniteFeatureName}.getTolerance().setValueAndUnits(1.0E-5, units_0);\n\n")

        macroFile.write(f"    {uniteFeatureName}.setUseAutoMatch(true);\n\n")
        macroFile.write(f"    {uniteFeatureName}.setKeepImprintedEdges(false);\n\n")
        macroFile.write(f"    {uniteFeatureName}.setTransferFaceNames(true);\n\n")
        macroFile.write(f"    {uniteFeatureName}.setTransferBodyNames(false);\n\n")

        # Emit body lookups with unique variable names
        body_vars = []
        for i, body_name in enumerate(bodyPresentationNames):
            var = f"cadmodelerBody_{i}"
            body_vars.append(var)
            macroFile.write(
                f'    star.cadmodeler.Body {var} = ((star.cadmodeler.Body) cadModel_0.getBody("{body_name}"));\n\n'
            )

        macroFile.write(
            f"    {uniteFeatureName}.setBodies(new ArrayList<>(Arrays.<Body>asList({', '.join(body_vars)})));\n\n"
        )

        macroFile.write(
            f"    {uniteFeatureName}.setBodyGroups(new ArrayList<>(Collections.<BodyGroup>emptyList()));\n\n"
        )
        macroFile.write(
            f"    {uniteFeatureName}.setCadFilters(new ArrayList<>(Collections.<CadFilter>emptyList()));\n\n"
        )
        macroFile.write(f"    {uniteFeatureName}.setApplyToAllInstances(false);\n\n")
        macroFile.write(
            f"    {uniteFeatureName}.setExcludedInstancedBodies(new ArrayList<>(Collections.<Body>emptyList()));\n\n"
        )
        macroFile.write(f"    {uniteFeatureName}.setIsBodyGroupCreation(false);\n\n")

        macroFile.write(
            f"    cadModel_0.getFeatureManager().markDependentNotUptodate({uniteFeatureName});\n\n"
        )
        macroFile.write(f"    cadModel_0.allowMakingPartDirty(true);\n\n")
        macroFile.write(f"    {uniteFeatureName}.markFeatureForEdit();\n\n")
        macroFile.write(f"    cadModel_0.getFeatureManager().execute({uniteFeatureName});\n\n")
