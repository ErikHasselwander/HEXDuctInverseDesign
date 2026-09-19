// Simcenter STAR-CCM+ macro: save.java
// Written by Simcenter STAR-CCM+ 19.06.009
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;

public class save extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {
    Simulation simulation_0 = 
      getActiveSimulation();
    simulation_0.saveState("/scratch/erikhass/inversedesign/final_designs/it_197/case.sim");
  }

}
