def puntos():
    datosPuntos = pd.read_excel("CenVacGeoLocAllFieldsConoNorte.xlsx")#,header=None,sheet_name= "minutos")
    p=[]
    for i in datosPuntos["Centro"]:
        p.append(i)
    return p

def addDataRetorno(Matrix,final):
    vector=puntos();
    for i in vector:
         Matrix[i,final]=Matrix[i,vector[0]]
         Matrix[final,i]=Matrix[vector[0],i]
         Matrix[final,final]=0
    return Matrix
  
def dataXLS():
    import pandas as pd
    Matrix={}
    TIEMPOS_RECORRIDO = pd.read_excel("matrizDistancias.xlsx")
    TRAVEL_TIMES = TIEMPOS_RECORRIDO.values.tolist()
    cuenta =0
    VECTOR=[]
    for r in TRAVEL_TIMES:
        for index,c in enumerate(r):
            if index>0:
                VECTOR.append(c)
    VECTOR=tuple(VECTOR)
    
    cuenta=0
    for i in puntos():
        for j in puntos():
            Matrix[i,j]=VECTOR[cuenta]
            cuenta=cuenta+1
    return Matrix

import pandas as pd
def LocationXLS():
    global COORDX, COORDY
    global PESO
    COORDX={}
    COORDY={}
    PESO={}
    p=puntos()
    datosPuntos = pd.read_excel("CenVacGeoLocAllFieldsConoNorte.xlsx")#,header=None,sheet_name= "minutos")
    for r in datosPuntos.index:
        COORDX[p[r]]=datosPuntos['lng'][r]
        COORDY[p[r]]=datosPuntos['lat'][r]
        PESO[p[r]]=datosPuntos['Cantidad'][r]
    COORDX['RETORNO']=datosPuntos['lng'][0]
    COORDY['RETORNO']=datosPuntos['lat'][0]
    

from gurobipy import *
def resolver_VRP(cap):
    import gurobipy
    import os
    import sys
    import json, pandas as pd
    #global COORDX, COORDY, CAMION
    global Y
    global COORDX
    global COORDY
    global CAMION
    global PESO

    options = {
        "WLSACCESSID": "XXXXXXXXXXXXXXXXXXXXXXXX",
        "WLSSECRET": "XXXXXXXXXXXXXXXXXXXXXX",
        "LICENSEID": YYYYYY,
        }

    enviroment=Env(params=options)
    m = Model("model", env=enviroment)

    
       
    DESTINO=puntos()
    distancia=dataXLS()
    DESTINO.append("RETORNO")
    distancia=addDataRetorno(distancia,"RETORNO")

    X = {}
    CAMION={'XXX000'}
    Y = {}
    W = {}
    DEFCAP ={}

    U={}
    for c in CAMION:
        for d in DESTINO:
            U[c,d] = m.addVar(vtype=GRB.CONTINUOUS,  name = 'U_%s.%s' % (c,d))

    #Si sale el camión
    for i in CAMION:
        Y[i] = m.addVar(name='Y'+i,vtype=GRB.BINARY)
        DEFCAP[i]=m.addVar(name='DEFCAP'+i,vtype=GRB.CONTINUOUS)
        
    #Si el camión i va del destino j al destino k
    for i in CAMION:
        for j in DESTINO:
            for k in DESTINO:
                X[i,j,k] = m.addVar(name='X_'+str(i)+'_'+str(j)+'_'+str(k),vtype=GRB.BINARY)

    #Si se atiende el destino k            
    for k in DESTINO:
        W[k] = m.addVar(vtype=GRB.CONTINUOUS,name='W_%s' % (k))

    m.setObjective(quicksum(distancia[j,k]*X[i,j,k] for i in CAMION for j in DESTINO for k in DESTINO)
                   +10000*quicksum(DEFCAP[i] for i in CAMION)
                   +quicksum(U[i,j] for i in CAMION for j in DESTINO)  )
    m.modelSense = GRB.MINIMIZE

    #Para este caso salen todos los camiones
    m.addConstr(quicksum(Y[i] for i in CAMION)==len(CAMION))

    #Cada camión sale de punto de carga
    for i in CAMION:
        m.addConstr(quicksum(X[i,j,k] for index2,k in enumerate(DESTINO) for index3,j in enumerate(DESTINO) \
          if index2!=len(DESTINO)-1 and index2!=0 and index3==0) ==Y[i])

    for i in CAMION:
        m.addConstr(quicksum(X[i,k,j] for index2,k in enumerate(DESTINO) for index3,j in enumerate(DESTINO) \
          if index2!=len(DESTINO)-1 and index2!=0 and index3==len(DESTINO)-1) ==Y[i])

    #ningun camión sale del punto de llegada
    for i in CAMION:
        m.addConstr(quicksum(X[i,j,k] for index2,k in enumerate(DESTINO) for index3,j in enumerate(DESTINO) \
          if index2!=len(DESTINO)-1 and index2!=0 and index3==len(DESTINO)-1) ==0,name="C_%s" % (i))

    #no hay camino directo del origen al final      
    m.addConstr(quicksum(X[i,j,k] for i in CAMION \
          for index2,k in enumerate(DESTINO) for index3,j in enumerate(DESTINO) \
          if index2==len(DESTINO)-1 and index3==0) ==0,name="D_%s" % (i))

    #pasan por todos los destinos !!!ORIGINAL <=1 las restricciones 1 y 2
    for index1,j in enumerate(DESTINO):
        if index1!=len(DESTINO)-1 and index1!=0:
                m.addConstr(quicksum(X[i,j,k] for i in CAMION for k in DESTINO if j!=k) <=1,name="E_%s" % (i))

    for index1,k in enumerate(DESTINO): 
        if index1!=len(DESTINO)-1 and index1!=0:
                m.addConstr(quicksum(X[i,j,k] for i in CAMION for j in DESTINO if j!=k) <=1,name="F_%s" % (i))

    for index1,i in enumerate(CAMION):
        for index3,k in enumerate(DESTINO):
            if index3!=len(DESTINO)-1 and index3!=0:
                m.addConstr(quicksum(X[i,j,k] for j in DESTINO if j!=k) == quicksum(X[i,k,j] for j in DESTINO if j!=k),name="G_%s_%s" % (i,k))   

    #Malucelli
    for i in CAMION:
        for j in DESTINO:
            for k in DESTINO:
                if j!=k:
                    m.addConstr(U[i,k]<=U[i,j]+1-len(DESTINO)*(X[i,j,k]-1))
                    m.addConstr(U[i,k]>=U[i,j]+1+len(DESTINO)*(X[i,j,k]-1))

    #El orden del primer nodo es 0
    m.addConstr(quicksum(U[i,j] for i in CAMION for index2,j \
                 in enumerate(DESTINO) if index2==0) ==0,name="U1")

    for i in CAMION:
        for index2,j in enumerate(DESTINO):
            if index2==len(DESTINO)-1:
                m.addConstr(U[i,j]==quicksum(X[i,jj,k] for jj in DESTINO for k in DESTINO if jj!=k),name="U2_%s" % (i))
                
    for i in CAMION:
        m.addConstr(quicksum(PESO[j]*X[i,j,k] for index1,j in enumerate(DESTINO) for index2,k in enumerate(DESTINO)
                             if j!=k and index1!=len(DESTINO)-1 and index2!=len(DESTINO)-1) + DEFCAP[i]== cap*Y[i])

    m.optimize()
    #m.computeIIS()
    #print (m.display())
    m.write('model2.json')
    m.write('model2.lp')
    gv = m.getVars()
    for v in gv:
        if v.X>0:
            print(f"{v.VarName} ={v.X}")

    for c in CAMION:
            Y[c]=Y[c].X            

    
    
    file2=open('model2.json')
    data=json.load(file2)
    file2.close()

    LocationXLS()
    df=pd.DataFrame(columns=['CAMION', 'ORDEN', 'CENTRO','LATITUD','LONGITUD'])
    new_index=0
    route={}
    for c in CAMION:
        route={}
        if Y[c]==1:
            for linea in data['Vars']:
                if "U_" in linea['VarName'] and c in linea['VarName']:
                    print(linea['VarName'],linea)
                    centro=linea['VarName']
                    punto1=centro.index('.')
                    cod_centro = centro[punto1+1:]
                    if cod_centro[0].isdecimal():
                        cod_centro1=str(cod_centro)
                    else:
                        cod_centro1=cod_centro
                    route[int(linea['X'])]=(cod_centro1,COORDX[cod_centro1],COORDY[cod_centro1])
                    df.loc[new_index] = [c, round(linea['X']),cod_centro1,COORDX[cod_centro1],COORDY[cod_centro1]]  # New student's marks
                    new_index = df.index.max() + 1
        route=dict(sorted(route.items()))
        print(route)
    return df

def crear_ruta_de_data():
    import json
    global COORDX, COORDY, CAMION
    
    file2=open('model2.json')
    data=json.load(file2)
    file2.close()

    LocationXLS()
    
    diccionario={}
    route={}
    for c in CAMION:
        route={}
        if Y[c]==1:
            for linea in data['Vars']:
                if "U_" in linea['VarName'] and c in linea['VarName']:
                    centro=linea['VarName']
                    punto1=centro.index('.')
                    cod_centro = centro[punto1+1:]
                    if cod_centro[0].isdecimal():
                        cod_centro1=str(cod_centro)
                    else:
                        cod_centro1=cod_centro
                    route[int(linea['X'])]=(cod_centro1,COORDX[cod_centro1],COORDY[cod_centro1])
        route=dict(sorted(route.items()))
        diccionario[c]=route
    return diccionario           



import pandas as pd
capacidad=500
LocationXLS()
resolver_VRP(capacidad)
global COORDX, COORDY
COORDX={}
COORDY={}
df=pd.DataFrame()
a=crear_ruta_de_data()
b=crear_dataframe_de_data()
print (b.to_string())

