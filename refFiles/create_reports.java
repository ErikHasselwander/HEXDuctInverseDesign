// Simcenter STAR-CCM+ macro: create_reports.java
// Written by Simcenter STAR-CCM+ 19.06.009
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;
import star.base.report.*;
import star.flow.*;

public class create_reports extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {

    // --- EDIT HERE: add as many entries as you want ---
    // { part_name, part_surface, part_surface_display_name }
    String[][] INPUTS = new String[][] {
      { "inlet", "hex_inlet_interface [hex/inlet]", "hex_inlet" },
      { "outlet", "hex_outlet_interface [hex/outlet]", "hex_outlet" },
      // { "outlet", "outlet", "outlet" },
      // { "whatever", "some_boundary_name", "nice_display_name" },
    };
    // --- END EDIT AREA ---

    Simulation simulation_0 =
      getActiveSimulation();

    for (String[] in : INPUTS) {

      String part_name = in[0];
      String part_surface = in[1];
      String part_surface_display_name = in[2];  // currently unused, but available
      // (keep the rest of your code exactly as-is below)

      MassFlowAverageReport massFlowAverageReport_0 =
        simulation_0.getReportManager().create("star.flow.MassFlowAverageReport");

      PrimitiveFieldFunction primitiveFieldFunction_0 =
        ((PrimitiveFieldFunction) simulation_0.getFieldFunctionManager().getFunction("AbsoluteTotalPressure"));

      massFlowAverageReport_0.setFieldFunction(primitiveFieldFunction_0);

      massFlowAverageReport_0.getParts().setQuery(null);

      Region region_0 =
        simulation_0.getRegionManager().getRegion("Composite." + part_name);

      Boundary boundary_0 =
        region_0.getBoundaryManager().getBoundary(part_surface);

      massFlowAverageReport_0.getParts().setObjects(boundary_0);

      massFlowAverageReport_0.setPresentationName("p0_" + part_name + "_" + part_surface_display_name);

      MassFlowAverageReport massFlowAverageReport_1 =
        simulation_0.getReportManager().create("star.flow.MassFlowAverageReport");

      PrimitiveFieldFunction primitiveFieldFunction_1 =
        ((PrimitiveFieldFunction) simulation_0.getFieldFunctionManager().getFunction("TotalTemperature"));

      massFlowAverageReport_1.setFieldFunction(primitiveFieldFunction_1);

      massFlowAverageReport_1.getParts().setQuery(null);

      massFlowAverageReport_1.getParts().setObjects(boundary_0);

      massFlowAverageReport_1.setPresentationName("T0_" + part_name + "_" + part_surface_display_name);

      AreaAverageReport areaAverageReport_0 =
        simulation_0.getReportManager().create("star.base.report.AreaAverageReport");

      PrimitiveFieldFunction primitiveFieldFunction_2 =
        ((PrimitiveFieldFunction) simulation_0.getFieldFunctionManager().getFunction("AbsolutePressure"));

      areaAverageReport_0.setFieldFunction(primitiveFieldFunction_2);

      areaAverageReport_0.getParts().setQuery(null);

      areaAverageReport_0.getParts().setObjects(boundary_0);

      areaAverageReport_0.setPresentationName("p_" + part_name + "_" + part_surface_display_name);

      MassFlowAverageReport massFlowAverageReport_2 =
        simulation_0.getReportManager().create("star.flow.MassFlowAverageReport");

      PrimitiveFieldFunction primitiveFieldFunction_3 =
        ((PrimitiveFieldFunction) simulation_0.getFieldFunctionManager().getFunction("Velocity"));

      VectorMagnitudeFieldFunction vectorMagnitudeFieldFunction_0 =
        ((VectorMagnitudeFieldFunction) primitiveFieldFunction_3.getMagnitudeFunction());

      massFlowAverageReport_2.setFieldFunction(vectorMagnitudeFieldFunction_0);

      massFlowAverageReport_2.setPresentationName("v_" + part_name + "_" + part_surface_display_name);

      massFlowAverageReport_2.getParts().setQuery(null);

      massFlowAverageReport_2.getParts().setObjects(boundary_0);

    } // end loop
  }
}