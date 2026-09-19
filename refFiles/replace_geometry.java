// Simcenter STAR-CCM+ macro: replace_geometry.java
// Written by Simcenter STAR-CCM+ 19.02.013
package macro;

import java.util.*;
import star.base.neo.*;
import star.cadmodeler.*;
import star.common.*;
import star.meshing.*;

import java.text.SimpleDateFormat;
import java.util.Date;


public class replace_geometry extends StarMacro {
  public void execute() {
    execute0();
  }

  private void execute0() {
    Simulation simulation_0 = getActiveSimulation();

    CadModel cadModel_0 = ((CadModel) simulation_0.get(SolidModelManager.class).getObject("geometry"));

    star.cadmodeler.Body cadmodelerBody_0 = ((star.cadmodeler.Body) cadModel_0.getBody("inlet"));

    star.cadmodeler.Body cadmodelerBody_1 = ((star.cadmodeler.Body) cadModel_0.getBody("hex"));

    star.cadmodeler.Body cadmodelerBody_2 = ((star.cadmodeler.Body) cadModel_0.getBody("outlet"));

    cadModel_0.createParts(new ArrayList<>(Arrays.<Body>asList(cadmodelerBody_0, cadmodelerBody_1, cadmodelerBody_2)), new ArrayList<>(Collections.<BodyGroup>emptyList()), true, false, 1, false, false, 3, "SharpEdges", 30.0, 4, true, 1.0E-5, false);

    CompositePart compositePart_0 = ((CompositePart) simulation_0.get(SimulationPartManager.class).getPart("Composite"));

    SolidModelPart solidModelPart_0 = ((SolidModelPart) compositePart_0.getChildParts().getPart("hex"));

    SolidModelPart solidModelPart_1 = ((SolidModelPart) compositePart_0.getChildParts().getPart("inlet"));

    SolidModelPart solidModelPart_2 = ((SolidModelPart) compositePart_0.getChildParts().getPart("outlet"));

    compositePart_0.getChildParts().removeObjects(solidModelPart_0, solidModelPart_1, solidModelPart_2);

    SolidModelPart solidModelPart_3 = ((SolidModelPart) simulation_0.get(SimulationPartManager.class).getPart("hex"));

    SolidModelPart solidModelPart_4 = ((SolidModelPart) simulation_0.get(SimulationPartManager.class).getPart("inlet"));

    SolidModelPart solidModelPart_5 = ((SolidModelPart) simulation_0.get(SimulationPartManager.class).getPart("outlet"));

    compositePart_0.getChildParts().reparentParts(new ArrayList<>(Arrays.<GeometryPart>asList(solidModelPart_3, solidModelPart_4, solidModelPart_5)), compositePart_0.getChildParts());

    SolidModelPart solidModelPart_6 = ((SolidModelPart) compositePart_0.getChildParts().getPart("hex"));

    PrepareFor2dOperation prepareFor2dOperation_0 = ((PrepareFor2dOperation) simulation_0.get(MeshOperationManager.class).getObject("Badge for 2D Meshing"));

    prepareFor2dOperation_0.execute();

    Region region_0 = simulation_0.getRegionManager().getRegion("Composite.hex");

    region_0.getPartGroup().setQuery(null);

    region_0.getPartGroup().setObjects(solidModelPart_3);

    Region region_1 = simulation_0.getRegionManager().getRegion("Composite.inlet");

    region_1.getPartGroup().setQuery(null);

    region_1.getPartGroup().setObjects(solidModelPart_4);

    Region region_2 = simulation_0.getRegionManager().getRegion("Composite.outlet");

    region_2.getPartGroup().setQuery(null);

    region_2.getPartGroup().setObjects(solidModelPart_5);
  
    execute1();

    AutoMeshOperation2d autoMeshOperation2d_0 = ((AutoMeshOperation2d) simulation_0.get(MeshOperationManager.class).getObject("Automated Mesh (2D)"));

    autoMeshOperation2d_0.execute();
    
    String timeStamp = new SimpleDateFormat("HH:mm").format(new Date());

    System.out.println("[" + timeStamp + "] " + simulation_0.getPresentationName() + ": Meshing successful");
  }

  private void execute1() {

    Simulation simulation_0 = 
      getActiveSimulation();

    AutoMeshOperation2d autoMeshOperation2d_0 = 
      ((AutoMeshOperation2d) simulation_0.get(MeshOperationManager.class).getObject("Automated Mesh (2D)"));

    SurfaceCustomMeshControl surfaceCustomMeshControl_0 = 
      ((SurfaceCustomMeshControl) autoMeshOperation2d_0.getCustomMeshControls().getObject("Surface Control"));

    surfaceCustomMeshControl_0.getGeometryObjects().setQuery(null);

    CompositePart compositePart_0 = 
      ((CompositePart) simulation_0.get(SimulationPartManager.class).getPart("Composite"));

    SolidModelPart solidModelPart_0 = 
      ((SolidModelPart) compositePart_0.getChildParts().getPart("hex"));

    PartSurface partSurface_0 = 
      ((PartSurface) solidModelPart_0.getPartSurfaceManager().getPartSurface("hex_inlet_interface"));

    PartSurface partSurface_3 = 
      ((PartSurface) solidModelPart_0.getPartSurfaceManager().getPartSurface("hex_outlet_interface"));

    SolidModelPart solidModelPart_1 = 
      ((SolidModelPart) compositePart_0.getChildParts().getPart("inlet"));

    PartSurface partSurface_1 = 
      ((PartSurface) solidModelPart_1.getPartSurfaceManager().getPartSurface("hex_inlet_interface"));

    SolidModelPart solidModelPart_2 = 
      ((SolidModelPart) compositePart_0.getChildParts().getPart("outlet"));

    PartSurface partSurface_2 = 
      ((PartSurface) solidModelPart_2.getPartSurfaceManager().getPartSurface("hex_outlet_interface"));

    surfaceCustomMeshControl_0.getGeometryObjects().setObjects(partSurface_0, partSurface_1, partSurface_2, partSurface_3);
  }

}
