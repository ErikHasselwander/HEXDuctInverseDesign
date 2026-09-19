package macro;
import java.util.*;
import star.common.*;
import star.base.neo.*;

public class update_variables extends StarMacro {
  public void execute() {
    execute0();
  }

  private void execute0() {
    Simulation simulation_0 = getActiveSimulation();

    ScalarGlobalParameter scalarGlobalParameter_0 = ((ScalarGlobalParameter) simulation_0.get(GlobalParameterManager.class).getObject("kp"));
    scalarGlobalParameter_0.getQuantity().setValue(0);

  }
}
