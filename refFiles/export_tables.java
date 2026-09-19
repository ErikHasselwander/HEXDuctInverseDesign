// Simcenter STAR-CCM+ macro: export_tables.java
// Written by Simcenter STAR-CCM+ 19.06.009
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;

public class export_tables extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {

    Simulation simulation_0 = 
      getActiveSimulation();

    XyzInternalTable xyzInternalTable_0 = 
      ((XyzInternalTable) simulation_0.getTableManager().getTable("lower_diff_p"));

    xyzInternalTable_0.extract();

    xyzInternalTable_0.export("/scratch/erikhass/inversedesign/basecase_lower_diff_pressures_0.csv", ",");
  }
}
