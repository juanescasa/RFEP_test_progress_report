# -*- coding: utf-8 -*-
"""
Created on Wed May 26 12:08:30 2021

@author: calle
"""
import gurobipy as gp
from gurobipy import GRB
import sys

def solve_rfep(sNodesVehiclesPaths,
                sStationsVehiclesPaths,
                sOriginalStationsOwn,
                sOriginalStationsPotential,
                sSuppliers,
                sSuppliersRanges,
                sOriginVehiclesPaths,
                sDestinationVehiclesPaths,
                sSequenceNodesNodesVehiclesPaths,
                sFirstStationVehiclesPaths,
                sNotFirstStationVehiclesPaths,
                sNodesPotentialNodesOriginalVehiclesPaths,
                sOriginalStationsMirrorStations,
                sStationsSuppliers,
                sSuppliersWithDiscount,
                sRanges,
                pStartInventory = 0,
                pTargetInventory = 0,
                pSafetyStock = 0,
                pTankCapacity = 0,
                pMinRefuel = 0,
                pConsumptionMainRoute = 0,
                pConsumptionOOP = 0,
                pQuantityVehicles = 0,
                pStationCapacity = 0,
                pStationUnitCapacity = 0,
                pMinimumPurchaseQuantity = 0,
                pLowerQuantityDiscount = 0,
                pUpperQuantityDiscount = 0,
                pPrice = 0,
                pOpportunityCost = 0,
                pVariableCost = 0,
                pDistanceOOP = 0,
                pCostUnitCapacity = 0,
                pDiscount = 0,
                pLocationCost = 0,
                isONvInventory = False,
                isONvRefuelQuantity = False,
                isONvRefuel = False,
                isONvQuantityUnitsCapacity = False,
                isONvLocate = False,
                isONvQuantityPurchased = False,
                isONvQuantityPurchasedRange = False,
                isONvPurchasedRange = False,
                isONcInitialInventory = False,
                isONcTargetInventory = False,
                isONcMinInventory = False,
                isONcLogicRefuel1 = False,
                isONcLogicRefuel2 = False,
                isONcMaxRefuel = False,
                isONcInventoryBalance1 = False,
                isONcInventoryBalance2 = False,
                isONcInventoryBalance3 = False,
                isONcLogicLocation = False,
                isONcLogicLocation2 = False,
                isONcStationCapacity = False,
                isONcQuantityPurchased = False,
                isONcMinimumQuantitySupplier = False,
                isONcMinQuantityRange = False,
                isONcMaxQuantityRange = False,
                isONcUniqueQuantityRange = False,
                isONcUniqueRange = False,
                isONtotalRefuellingCost= False,
                isONtotalLocationCost= False,
                isONtotalDiscount= False):

    m = gp.Model()
    
    #Define variables
    if isONvInventory:
        vInventory = m.addVars(sNodesVehiclesPaths, name = 'vInventory')
    if isONvRefuelQuantity:
        vRefuelQuantity = m.addVars(sStationsVehiclesPaths, name = 'vRefuelQuantity')
    if isONvRefuel:
        vRefuel = m.addVars(sStationsVehiclesPaths, vtype = GRB.BINARY, name = 'vRefuel')
    if isONvQuantityUnitsCapacity:
        vQuantityUnitsCapacity = m.addVars(sOriginalStationsOwn, vtype = GRB.INTEGER, name = 'vQuantityUnitsCapacity')
    if isONvLocate:
        vLocate = m.addVars(sOriginalStationsPotential, vtype = GRB.BINARY, name = 'vLocate')
    if isONvQuantityPurchased:
        vQuantityPurchased = m.addVars(sSuppliers, name = 'vQuantityPurchased')
    if isONvQuantityPurchasedRange:
        vQuantityPurchasedRange = m.addVars(sSuppliersRanges, name = 'vQuantityPurchasedRange')
    if isONvPurchasedRange:
        vPurchasedRange = m.addVars(sSuppliersRanges, vtype = GRB.BINARY, name='vPurchasedRange')
    
    #Define Constraints
    #Refuelling Logic Constraints
    if isONcInitialInventory:
        cInitialInventory = m.addConstrs((vInventory[i,v,p]==pStartInventory[v,p] 
                                      for (i,v,p) in sOriginVehiclesPaths), name = 'initialInventory')
    if isONcTargetInventory:
        cTargetInventory = m.addConstrs((vInventory[i,v,p]==pTargetInventory[v,p] 
                                      for (i,v,p) in sDestinationVehiclesPaths), name = 'targetInventory')
    if isONcTargetInventory:
        cMinInventory = m.addConstrs((vInventory[i,v,p]>=pSafetyStock[v] 
                                   for (i,v,p) in sStationsVehiclesPaths), name ='minInventory')
    if isONcLogicRefuel1:
        cLogicRefuel1 = m.addConstrs((vRefuelQuantity[i,v,p]<=(pTankCapacity[v]-pSafetyStock[v])*vRefuel[i,v,p] 
                                   for (i,v,p) in sStationsVehiclesPaths), name = 'logicRefuel1')
    if isONcLogicRefuel2:
        cLogicRefuel2 = m.addConstrs((vRefuelQuantity[i,v,p]>=pMinRefuel[v]*vRefuel[i,v,p]
                                   for (i,v,p) in sStationsVehiclesPaths), name = 'logicRefuel2')
    if isONcMaxRefuel:
        cMaxRefuel = m.addConstrs((vInventory[i,v,p] + vRefuelQuantity[i,v,p] <= pTankCapacity[v] 
                                for (i,v,p) in sStationsVehiclesPaths), name = 'maxRefuel')
    if isONcInventoryBalance1:
        cInventoryBalance1 = m.addConstrs((vInventory[j,v,p] == pStartInventory[v,p] - (pConsumptionMainRoute[i,j,v,p] + pConsumptionOOP[j,v,p]*vRefuel[j,v,p]) 
                                        for (i,j,v,p) in sSequenceNodesNodesVehiclesPaths if (j,v,p) in sFirstStationVehiclesPaths), name = 'inventoryBalance1')
    if isONcInventoryBalance2:
        cInventoryBalance2 = m.addConstrs((vInventory[j,v,p] == vInventory[i,v,p] + vRefuelQuantity[i,v,p] - 
                   (pConsumptionOOP[i,v,p]*vRefuel[i,v,p] + pConsumptionMainRoute[i,j,v,p] + pConsumptionOOP[j,v,p]*vRefuel[j,v,p]) 
                   for (i,j,v,p) in sSequenceNodesNodesVehiclesPaths if (j,v,p) in sNotFirstStationVehiclesPaths), name = 'inventoryBalance2')
    if isONcInventoryBalance3:
        cInventoryBalance3 = m.addConstrs((vInventory[j,v,p]==vInventory[i,v,p]+vRefuelQuantity[i,v,p] - (pConsumptionMainRoute[i,j,v,p] + pConsumptionOOP[i,v,p]*vRefuel[i,v,p]) 
                                       for (i,j,v,p) in sSequenceNodesNodesVehiclesPaths if (j,v,p) in sDestinationVehiclesPaths), name = 'inventoryBalance3')
    # #Location Logic Constraints
    if isONcLogicLocation:
        cLogicLocation = m.addConstrs((vRefuel[j,v,p] <= vLocate[i] for (j,i,v,p) in sNodesPotentialNodesOriginalVehiclesPaths), name = 'logicLocation')
    # #Valid Inequality
    if isONcLogicLocation2:
        cLogicLocation2 = m.addConstrs((vRefuelQuantity[j,v,p] <= (pTankCapacity[v]-pSafetyStock[v])*vLocate[i] for (j,i,v,p) in sNodesPotentialNodesOriginalVehiclesPaths), name = 'logicLocation2')
    if isONcStationCapacity:
        cStationCapacity = m.addConstrs(((gp.quicksum(pQuantityVehicles[v,p] * vRefuelQuantity[j,v,p] for (j,v,p) in sStationsVehiclesPaths if (i,j) in sOriginalStationsMirrorStations))
                                      <=pStationCapacity[i] + pStationUnitCapacity[i]*vQuantityUnitsCapacity[i]  for i in sOriginalStationsOwn), name = 'stationCapacity')
    # #Supplier Logic constraints
    if isONcQuantityPurchased:
        cQuantityPurchased = m.addConstrs((vQuantityPurchased[l] == gp.quicksum(pQuantityVehicles[v,p]*vRefuelQuantity[i,v,p] for (i,v,p) in sStationsVehiclesPaths if (i,l) in sStationsSuppliers) for l in sSuppliers), name = 'quantityPurchased')
    if isONcMinimumQuantitySupplier:
        cMinimumQuantitySupplier = m.addConstrs((vQuantityPurchased[l]>=pMinimumPurchaseQuantity[l] for l in sSuppliers), name = 'minimumQuantitySupplier')
    if isONcMinQuantityRange:
        cMinQuantityRange = m.addConstrs((vQuantityPurchasedRange[l,g]>= vPurchasedRange[l,g]*pLowerQuantityDiscount[l,g] for (l,g) in sSuppliersRanges), name = 'minQuantityRange')
    if isONcMaxQuantityRange:
        cMaxQuantityRange = m.addConstrs((vQuantityPurchasedRange[l,g]<= vPurchasedRange[l,g]*pUpperQuantityDiscount[l,g] for (l,g) in sSuppliersRanges), name = 'maxQuantityRange')
    if isONcUniqueQuantityRange:
        cUniqueQuantityRange = m.addConstrs((gp.quicksum(vQuantityPurchasedRange[l,g] for g in sRanges if (l,g) in sSuppliersRanges) == vQuantityPurchased[l] for l in sSuppliersWithDiscount), name = 'uniqueQuantityRange')
    if isONcUniqueRange:
        cUniqueRange = m.addConstrs((gp.quicksum(vPurchasedRange[l,g] for g in sRanges if (l, g) in sSuppliersRanges) == 1 for l in sSuppliersWithDiscount), name = 'uniqueRange')
    
    #Objective Function
    if isONtotalRefuellingCost:
        totalRefuellingCost = gp.quicksum(pQuantityVehicles[v,p]*(vRefuelQuantity[i,v,p]*pPrice[i] + (pOpportunityCost[v] + 2*pVariableCost[v]*pDistanceOOP[i,p])*vRefuel[i,v,p])  
                                       for (i,v,p) in sStationsVehiclesPaths)
    else:
        totalRefuellingCost = 0
    
    if isONtotalLocationCost:
        totalLocationCost = gp.quicksum(pLocationCost[i]*vLocate[i] for i in sOriginalStationsPotential) + gp.quicksum(pCostUnitCapacity[i]*vQuantityUnitsCapacity[i] for i in sOriginalStationsOwn)
    else:
        totalLocationCost = 0
    
    if isONtotalDiscount:
        totalDiscount = gp.quicksum(pDiscount[l,g]*vQuantityPurchasedRange[l,g] for (l,g) in sSuppliersRanges)
    else:
        totalDiscount=0
    m.setObjective(totalRefuellingCost + totalLocationCost - totalDiscount, GRB.MINIMIZE )
    #m.setObjective(0, GRB.MINIMIZE )
    #This allows to get a definitive conclusion between unbounded or infeasible model.
    m.Params.DualReductions = 0
    #l_time_track.append(('start_optimization', time.time()))
    m.optimize()
    #l_time_track.append(('start_export_output', time.time()))
    #Dealing with infeasability
    status = m.status
    if status == GRB.INFEASIBLE:
        print("The model is infeasible")
        m.computeIIS()
        for c in m.getConstrs():
            if c.IISConstr:
                print('%s' % c.constrName)
        #this stop the execution of this file.
        sys.exit()
    
    if isONvInventory:
        ovInventory = m.getAttr('x', vInventory)
    else:
        ovInventory = 0
        
    if isONvRefuelQuantity:
        ovRefuelQuantity = m.getAttr('x', vRefuelQuantity)
    else:
        ovRefuelQuantity = 0    
        
    if isONvRefuel:
        ovRefuel = m.getAttr('x', vRefuel)
    else:
        ovRefuel = 0
    
    if isONvQuantityUnitsCapacity:
        ovQuantityUnitsCapacity = m.getAttr('x', vQuantityUnitsCapacity)
    else:
        ovQuantityUnitsCapacity = 0
    
    if isONvLocate:
        ovLocate = m.getAttr('x', vLocate)
    else:
        ovLocate = 0
    
    if isONvQuantityPurchasedRange:
        ovQuantityPurchased = m.getAttr('x', vQuantityPurchased)
    else:
        ovQuantityPurchased = 0
    
    if isONvQuantityPurchasedRange:
        ovQuantityPurchasedRange = m.getAttr('x', vQuantityPurchasedRange)
    else:
        ovQuantityPurchasedRange = 0
        
    if isONvPurchasedRange:
        ovPurchasedRange = m.getAttr('x', vPurchasedRange)
    else:
        ovPurchasedRange = 0
    
    if isONtotalRefuellingCost:
        oTotalRefuellingCost = sum(pQuantityVehicles[v,p]*(ovRefuelQuantity[i,v,p]*pPrice[i] + (pOpportunityCost[v] + 2*pVariableCost[v]*pDistanceOOP[i,p])*ovRefuel[i,v,p])  
                                       for (i,v,p) in sStationsVehiclesPaths)
    else:
        oTotalRefuellingCost = 0
    
    if isONtotalLocationCost:
        oTotalLocationCost = sum(pLocationCost[i]*ovLocate[i] for i in sOriginalStationsPotential) + sum(pCostUnitCapacity[i]*ovQuantityUnitsCapacity[i] for i in sOriginalStationsOwn)
    else:
        oTotalLocationCost = 0
    
    if isONtotalDiscount:
        oTotalDiscount = sum(pDiscount[l,g]*ovQuantityPurchasedRange[l,g] for (l,g) in sSuppliersRanges)
    else:
        oTotalDiscount = 0
        
    oTotalCost = oTotalRefuellingCost + oTotalLocationCost - oTotalDiscount
    
    #n_vehicles=len(df_vehicles_paths['COD_VEHICLE'].unique())
    #n_paths=len(df_vehicles_paths['COD_PATH'].unique())
    #n_avg_stations_path = df_nodes_paths.groupby('COD_PATH')['COD_NODE1'].count().subtract(2).mean()
    #n_candidate_locations = len(sOriginalStationsPotential)
    
    n_constraints = m.NumConstrs
    n_variables = m.Numvars
    n_integer_variables = m.NumIntVars
    n_binary_variables = m.NumBinVars
    model_fingerprint = m.Fingerprint
    model_runtime = m.Runtime
    model_MIPGap = m.Mipgap
    
    return(status,
            ovInventory,
            ovRefuelQuantity,
            ovRefuel,
            ovQuantityUnitsCapacity,
            ovLocate,
            ovQuantityPurchased,
            ovQuantityPurchasedRange,
            ovPurchasedRange,
            oTotalRefuellingCost,
            oTotalLocationCost,
            oTotalDiscount,
            oTotalCost,
            n_constraints,
            n_variables,
            n_integer_variables,
            n_binary_variables,
            model_fingerprint,
            model_runtime,
            model_MIPGap)
