// STAR-CCM+ macro: Report_to_csv.java
package macro;

import java.io.*;
import java.nio.*;
import java.util.*;
import star.base.neo.*;
import star.base.report.*;
import star.common.*;
import star.flow.*;
import star.vis.*;
import star.meshing.*;
import star.cadmodeler.*;

public class post_star extends StarMacro {
  BufferedWriter bwout = null;

  public void execute() {
    export_figures();
    export_reports();
    export_tables();
    clear_save();
  }

  private void export_figures() {
    Simulation simulation_0 = getActiveSimulation();
    String outPutDir = simulation_0.getSessionDir();

    for (StarPlot plot : simulation_0.getPlotManager().getPlots()) {
      plot.openInteractive();
      String filePath = outPutDir + "/" + "plot_" + plot.getPresentationName() + ".png";
      plot.encode(resolvePath(filePath), "png", 800, 600, true, true);
      simulation_0.println("Saved: " + filePath);
    }

    for (Scene scene : simulation_0.getSceneManager().getScenes()) {
      String filePath = outPutDir + "/" + scene.getPresentationName() + ".png";
      scene.resetCamera();
      scene.printAndWait(resolvePath(filePath), 1, 1280, 720);
      simulation_0.println("Saved: " + filePath);
    }
  }

  public void export_reports() {
    try {
      Simulation simulation_0 = getActiveSimulation();

      // Collecting the simualtion file name
      String simulationName = simulation_0.getPresentationName();
      simulation_0.println("Simulation Name:" + simulationName);

      // Open Buffered Input and Output Readers
      // Creating file with name "<sim_file_name>+report.csv"
      BufferedWriter bwout = new BufferedWriter(new FileWriter(resolvePath(simulation_0.getSessionDir() + "/" + "results.csv")));
      bwout.write("Report Name, Value\n");

      Collection<Report> reportCollection = simulation_0.getReportManager().getObjects();

      for (Report thisReport : reportCollection) {
        String fieldLocationName = thisReport.getPresentationName();
        Double fieldValue = thisReport.getReportMonitorValue();
        String fieldUnits = thisReport.getUnits().toString();

        // Write Output file as "sim file name"+report.csv
        bwout.write(fieldLocationName + ", " + fieldValue + "\n");
      }

      Collection<Monitor> monitors = simulation_0.getMonitorManager().getObjects();
      for (Monitor monitor : monitors) {
        if (monitor instanceof ResidualMonitor) {
          ResidualMonitor residualMonitor = (ResidualMonitor) monitor;

          double[] residualValues = residualMonitor.getAllYValues();

          if (residualValues.length > 0) {
            double lastValue = residualValues[residualValues.length - 1];
            bwout.write(residualMonitor.getPresentationName() + ", " + lastValue + "\n");
          }
        }
      }

      bwout.close();

    } catch (IOException iOException) {
    }
  }

  private void export_tables() {

    Simulation simulation_0 = getActiveSimulation();
    String outPutDir = simulation_0.getSessionDir();

    Collection<Table> tableCollection = simulation_0.getTableManager().getObjects();

    // Loop over ALL tables in the Table Manager
    for (Table table : tableCollection) {

      // Build output filename with no leading path
      String filePath = outPutDir + "/" + table.getPresentationName() + ".csv";

      if (table instanceof XyzInternalTable) {
        FvRepresentation fvRepresentation_0 =
          ((FvRepresentation) simulation_0.getRepresentationManager().getObject("Volume Mesh"));
        ((XyzInternalTable) table).setRepresentation(fvRepresentation_0);
      }

      // If it's an internal table, it needs extracting before export
      if (table instanceof InternalTable) {
        ((InternalTable) table).extract();
      }

      // Export as CSV (comma-separated)
      table.export(resolvePath(filePath), ",");

      simulation_0.println("Saved: " + filePath);
    }
  }


  private void clear_save() {

    Simulation simulation_0 = 
      getActiveSimulation();

    String filePath = simulation_0.getSessionDir() + "/" + "case.sim";

    Solution solution_0 = 
      simulation_0.getSolution();

    solution_0.clearSolution(Solution.Clear.History, Solution.Clear.Fields, Solution.Clear.LagrangianDem);

    MeshPipelineController meshPipelineController_0 = 
      simulation_0.get(MeshPipelineController.class);

    meshPipelineController_0.clearGeneratedMeshes();

    simulation_0.saveState(resolvePath(filePath));

    CadModel cadModel_0 = 
      ((CadModel) simulation_0.get(SolidModelManager.class).getObject("geometry"));

    simulation_0.get(SolidModelManager.class).removeObjects(cadModel_0);
  }

}
