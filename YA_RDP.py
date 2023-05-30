####################################################
##### Calculo de redeterminaciones definitivas de precios #####
####################################################
# Se agrega validacion por escalamiento del 4%
# Niveles de ajuste:
"""
1 - Jerarquia / Insumo / Moneda
2 - Moneda
...
...
i - ..... / ..... / Moneda
"""

from psdi.server import MXServer
from java.text import SimpleDateFormat

if launchPoint == "YA_RDP":

	# Setear las variables globales
	mxServer = MXServer.getMXServer()
	userInfo = mbo.getUserInfo()
	conKey = userInfo.getConnectionKey()

	# Validar que se trata de un contrato de tipo avanzado
	avanzado = mbo.getBoolean("YA_CONTRATO_AVANZADO")
	status_contrato = mbo.getString("STATUS")
	n_contrato = mbo.getString("CONTRACTNUM")
	rev_contrato = mbo.getString("REVISIONNUM")

	if avanzado == 1 and status_contrato in ["APPR"]:
		# Defino error generico para calculo de redeterminaciones
		def setError(valor):
			global errorkey,errorgroup,params
			errorkey='generic'
			errorgroup='designer'
			params=[valor]
		# Defino error generico para calculo de redeterminaciones
		def setWarn(valor):
			global warnkey,warngroup,params
			warnkey='generic'
			warngroup='designer'
			params=[valor]
		# Seteo en 0 el error (error = 0 -> no hay errores)
		error = 0
		# Cantidad de decimales a redondear
		decimales = 4
		# Traigo tickets seleccionados
		lista_ticket_rdp = mbo.getMboSet("YA_RDP")
		cantidad_sel = lista_ticket_rdp.count()
		# Validar que se este ajustando solo un ticket a la vez
		if cantidad_sel == 0:
			setError("Por favor seleccione la solicitud de redeterminacion que desea calcular.") 
		elif cantidad_sel > 1:
			setError("Por favor seleccione solo 1 solicitud de redeterminacion para calcular.") 
		elif cantidad_sel == 1:
			ticket_rdp = lista_ticket_rdp.getMbo(0)
			if ticket_rdp is not None:
				# Traigo el numero de ticket
				ticket = ticket_rdp.getString("TICKETID")
				# Cancelo las redeterminaciones anteriores calculadas sobre ese ticket
				rdps_anteriores = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
				rdps_anteriores.setWhere(" ticketid = '" + ticket + "' and ya_status in ('INGRESADO','VAL_INGRESADO') ")
				rdps_anteriores.reset()
				for m in range (rdps_anteriores.count()):
					redeterminacion = rdps_anteriores.getMbo(m)
					if redeterminacion is not None:
						redeterminacion.setValue("YA_STATUS","DESESTIMADO")
				rdps_anteriores.save()
				# Traigo el periodo, clase y tipo del ticket
				spec_periodo = ticket_rdp.getMboSet("YA_SPEC_PERIODO").getMbo(0)
				spec_clase = ticket_rdp.getMboSet("YA_SPEC_CLASE").getMbo(0)
				spec_tipo = ticket_rdp.getMboSet("YA_SPEC_TIPO").getMbo(0)
				if spec_periodo is not None and spec_clase is not None and spec_tipo is not None:
					periodo = spec_periodo.getString("ALNVALUE")
					clase = spec_clase.getString("ALNVALUE")
					tipo = spec_tipo.getString("ALNVALUE")
					# Traigo periodo base del contrato
					periodo_base = mbo.getString("YA_PER_INDICE")                
					
					# Defino variable para saber si tengo que volver a correr el calculo por variacion del 4%
					var_menor_4 = 0
					
					
					if tipo == "PESOS":
						x = 2
						validacion = 1                  
					else:
						x = 1
						validacion = 0
						estado_creacion = "INGRESADO"
						
					for v in range (x):   
						if var_menor_4 == 0:
							
							clase = spec_clase.getString("ALNVALUE")
							
							if v == 0 and validacion == 1:
								nivel_ajuste = mbo.getString("YA_CLAVE_RDP_PROV")
								clase = "VALIDACION"
								estado_creacion = "VAL_INGRESADO"
							if v == 1 and validacion == 1:
								estado_creacion = "INGRESADO"
							
							# Redeterminacion tipo PESOS        
							if tipo == "PESOS":
								
								# Generales
												   
								# Redeterminacion DEFINITIVA                   
								if clase == "DEF":
									nivel_ajuste = mbo.getString("YA_CLAVE_RDP")
									
								# Redeterminacion PROVISORIA
								if clase == "PROV":
									nivel_ajuste = mbo.getString("YA_CLAVE_RDP_PROV")
									
								# RDP 1
								if nivel_ajuste == "1":
									combinaciones = mbo.getMboSet("YA_CLAVE_PESO1")
								# RDP 2
								if nivel_ajuste == "2":
									combinaciones = mbo.getMboSet("YA_CLAVE_PESO2")
								# RDP i
								
							   
							# Redeterminacion tipo OTRAS
							elif tipo == "OTRAS":           
								
								# Redeterminacion DEFINITIVA                   
								if clase == "DEF":     
									nivel_ajuste = mbo.getString("YA_CLAVE_RDP")
								
								# RDP 1
								if nivel_ajuste == "1":
									combinaciones = mbo.getMboSet("YA_CLAVE_NOPESO1")
								# RDP 2
								elif nivel_ajuste == "2":
									combinaciones = mbo.getMboSet("YA_CLAVE_NOPESO2")                    
								# RDP i 
								
							for z in range (combinaciones.count()):
								combinacion = combinaciones.getMbo(z)
								if combinacion is not None:    
									# Atributos Generales (aplica a todos los niveles de ajuste)
									contrato = combinacion.getString("CONTRACTNUM")
									revision = combinacion.getString("REVISIONNUM")
									moneda = combinacion.getString("YA_MONEDA")                       
									# Atributos RDP 1
									jerarquia = combinacion.getString("CLASSSTRUCTUREID")
									insumo = combinacion.getString("YA_INSUMO")        
									# Atributos RDP 2                       
									# Atributos RDP i
									
									
									# Variables Generales (aplica a todos los niveles de ajuste)
									lineas_contrato = mbo.getMboSet("CONTRACTLINE")                       
									
									# Variables RDP 1     
									if nivel_ajuste == "1":                    
										# Indices
										indices = combinacion.getMboSet("YA_POLINOMICA")
										# Lineas a la que se aplica la rdp
										lineas_precio = MXServer.getMXServer().getMboSet("contractline_precios", MXServer.getMXServer().getSystemUserInfo());
										lineas_precio.setWhere(" ya_insumo = '" + insumo + "' and ya_moneda = '" + moneda + "' and revisionnum = '" + revision + "' and contractnum = '" + contrato + "' and ya_insumo in (select ya_insumo from contract_insumos where contractnum = '" + contrato + "' and revisionnum = '" + revision + "' and ya_tipo_costo != '%CD') and contractlinenum in (select contractline.contractlinenum from contractline inner join contractline_precios on contractline.contractnum = contractline_precios.contractnum and contractline.revisionnum = contractline_precios.revisionnum and contractline.contractlinenum = contractline_precios.contractlinenum where contractline.contractlinenum in (select contractline.contractlinenum from classancestor inner join contractline on contractline.classstructureid = classancestor.classstructureid where ancestor = '" + jerarquia + "'))")
										lineas_precio.reset()                            
									
									# Variables RDP 2
									elif nivel_ajuste == "2":
										# Indices
										indices = combinacion.getMboSet("YA_POLINOMICA2")
										# Lineas a la que se aplica la rdp
										lineas_precio = MXServer.getMXServer().getMboSet("contractline_precios", MXServer.getMXServer().getSystemUserInfo());
										lineas_precio.setWhere(" ya_moneda = '" + moneda + "' and revisionnum = '" + revision + "' and contractnum = '" + contrato + "' and ya_insumo in (select ya_insumo from contract_insumos where contractnum = '" + contrato + "' and revisionnum = '" + revision + "' and ya_tipo_costo != '%CD') ")
										lineas_precio.reset()

									# Variables RDP i
									# Definir variable "indices" y variable "lineas_precio" (relacion ya_polinomicai y setWhere para contractline_precios) segun este definido el nivel de ajuste
										
									# Calculo de polinomica    
									resultado_polinomica = 0
									for y in range (indices.count()):
										indice = indices.getMbo(y)
										if indice is not None:
											indice1 = indice.getString("YA_INDICE")
											porc_incid = indice.getDouble("YA_PORC_INCIDENCIA")
											# Traigo los valores de los indices en el periodo del ticket
											valores = MXServer.getMXServer().getMboSet("INDICES_VALORES", MXServer.getMXServer().getSystemUserInfo());
											valores.setWhere(" ya_indice = '" + indice1 + "' and YA_PER_INDICE = '" + periodo + "' and status = 'PUBLICADO' ")
											valores.reset()
											valor = valores.getMbo(0)
											if valor is not None:
												valor_indice = valor.getDouble("YA_VALOR_INDICE")
												valores.save()
												# Traigo los valores de los indices en el periodo base
												valores_base = MXServer.getMXServer().getMboSet("INDICES_VALORES", MXServer.getMXServer().getSystemUserInfo());
												valores_base.setWhere(" ya_indice = '" + indice1 + "' and YA_PER_INDICE = '" + periodo_base + "' and status = 'PUBLICADO' ")
												valores_base.reset()
												valor_base = valores_base.getMbo(0)
												if valor_base is not None:
													valor_indice_base = valor_base.getDouble("YA_VALOR_INDICE")
													valores_base.save()
													# Calculo cada termino de la polinomica (cada indice)
													resultado_indice = round((porc_incid / 100) * valor_indice / valor_indice_base,decimales)
													# Calculo la polinomica (suma de cada indice)
													resultado_polinomica = round(resultado_polinomica + resultado_indice,decimales)                         
											else:
												error = 1                                     
												setError("El indice " + indice1 + " no tiene cargado el valor para el periodo de la solicitud. Por favor cargue ese valor y vuelva a calcular la redeterminacion." )
									if indices.count() == 0:
											error = 1                                     
											setError("Existe un nivel de ajuste sin indices cargados. Por favor cargue los indices que falten y vuelva a realizar el calculo." )                                               
								
										
									# Calculo de redeterminacion para costos directos                    
									for f in range (lineas_precio.count()):
										precio = lineas_precio.getMbo(f)
										if precio is not None:
											# Traigo cantidad de la linea
											linea = precio.getMboSet("YA_CONTRACTLINE").getMbo(0)
											if linea is not None:
												cantidad = linea.getDouble("ORDERQTY")                                
												precio_actual = precio.getDouble("YA_UNITCOST")
												# Calculo el precio unitario de redeterminacion
												precio_redeterminado = round(precio_actual * resultado_polinomica,decimales)
												# Calculo el precio de linea de redeterminacion
												precio_redeterminado_linea = round(precio_redeterminado * cantidad,decimales)
												# Traigo atributos de contractline_precios
												linea = precio.getString("CONTRACTLINENUM")
												insumo2 = precio.getString("YA_INSUMO")
												
												# Calculo de saldos
												# Traer cantidades de actas de mediciones anteriores
												strObject = "POLINE"
												strWhere =  "ponum in (select ponum from po where ya_tipo = 'FIS' and status = 'APROB' and YA_PERIODO < '" + periodo + "' ) and contreflineid in (select contractlineid from contractline where contractnum = '" + contrato + "' and contractlinenum = '" + linea + "')"
												actas_aprobadas_anteriores = mxServer.getMboSet(strObject, userInfo)
												actas_aprobadas_anteriores.setWhere(strWhere)
												actas_aprobadas_anteriores.reset()
												# Recorro cada AM y me traigo las cantidades
												cantidad_actas_aprobadas = 0
												for i in range (actas_aprobadas_anteriores.count()):
													acta_aprobada_anterior = actas_aprobadas_anteriores.getMbo(i)
													if acta_aprobada_anterior is not None:
														cantidad_acta = acta_aprobada_anterior.getDouble("ORDERQTY")
														# Defino la cantidad total
														cantidad_actas_aprobadas = round(cantidad_actas_aprobadas + cantidad_acta,decimales)
												# Defino el saldo de la linea
												saldo = round(cantidad - cantidad_actas_aprobadas,decimales)

												# Calculo de deltas para costos directos
												# Traer contractline_rdp anteriores de cada linea (por insumo y moneda)
												strObject = "CONTRACTLINE_RDP"
												if v == 0 and validacion == 1:
													strWhere =  "contractnum = '" + contrato + "' and revisionnum = '" + revision + "' and contractlinenum = '" + linea + "' and ya_insumo = '" + insumo2 + "' and ya_moneda = '" + moneda + "' and ya_periodo < '" + periodo + "' and ya_status = 'VAL_INGRESADO' and ya_clase = 'VALIDACION' and ticketid != '" + ticket + "' "
												elif (v == 1 and validacion == 1) or (validacion == 0):                                              
													strWhere =  "contractnum = '" + contrato + "' and revisionnum = '" + revision + "' and contractlinenum = '" + linea + "' and ya_insumo = '" + insumo2 + "' and ya_moneda = '" + moneda + "' and ya_periodo <= '" + periodo + "' and ya_status = 'APROB' and ya_clase in ('PROV','DEF') and ticketid != '" + ticket + "' "
												rdps_aprobadas_anteriores = mxServer.getMboSet(strObject, userInfo)
												rdps_aprobadas_anteriores.setWhere(strWhere)
												rdps_aprobadas_anteriores.reset()
												
												# Recorro cada RDP y me traigo el valor del DELTA
												deltas_anteriores = 0
												
												periodos_tomados = []
												
												for j in range (rdps_aprobadas_anteriores.count()):
													rdp_aprobada_anterior = rdps_aprobadas_anteriores.getMbo(j)
													if rdp_aprobada_anterior is not None:                                           
														delta = rdp_aprobada_anterior.getDouble("YA_DELTA_AJUSTE")
														# Defino la suma de los deltas anteriores
														deltas_anteriores = round(deltas_anteriores + delta,decimales)
												# Defino el delta total (El 1 corresponde al "DELTA" base)
												delta_total = round(resultado_polinomica - deltas_anteriores - 1,decimales)                                      

												# Calculo del incremento contractual
												incremento = round(saldo * delta_total * precio_actual,decimales)
												
												# Calculo del costo saldo de obra
												costo_saldo_obra = round(precio_redeterminado * saldo,decimales)
												
												# Agrego registro a contractline_rdp
												redeterminaciones = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
												redeterminaciones.reset()
												redeterminaciones_add = redeterminaciones.add()
												redeterminaciones_add.setValue("CONTRACTNUM",contrato)
												redeterminaciones_add.setValue("REVISIONNUM",revision)
												redeterminaciones_add.setValue("CONTRACTLINENUM",linea)
												redeterminaciones_add.setValue("YA_INSUMO",insumo2)
												redeterminaciones_add.setValue("YA_MONEDA",moneda)
												redeterminaciones_add.setValue("YA_CLASE",clase)
												redeterminaciones_add.setValue("YA_PERIODO",periodo)
												redeterminaciones_add.setValue("TICKETID",ticket)
												redeterminaciones_add.setValue("YA_STATUS",estado_creacion)
												redeterminaciones_add.setValue("YA_FECHA_CALCULO",MXServer.getMXServer().getDate())
												redeterminaciones_add.setValue("YA_UNITCOST_RDP",precio_redeterminado)
												redeterminaciones_add.setValue("YA_LINECOST_RDP",precio_redeterminado_linea)
												redeterminaciones_add.setValue("YA_DELTA_RDP",resultado_polinomica)
												redeterminaciones_add.setValue("YA_DELTA_AJUSTE",delta_total)
												redeterminaciones_add.setValue("YA_SALDO",saldo)
												redeterminaciones_add.setValue("YA_INCREMENTO",incremento)
												redeterminaciones_add.setValue("YA_COSTO_SALDO_OBRA",costo_saldo_obra)
												redeterminaciones.save()                                     
													   
							
							# Recalculo de insumos porcentuales
							# Recorro cada linea
							
							for g in range (lineas_contrato.count()):
								lineas = lineas_contrato.getMbo(g)
								if lineas is not None:
									linea3 = lineas.getString("CONTRACTLINENUM")
									contrato3 = lineas.getString("CONTRACTNUM")
									revision3 = lineas.getString("REVISIONNUM")
									cantidad3 = lineas.getDouble("ORDERQTY")
									# Recorro cada insumo porcentual
									contractline_insumos = lineas.getMboSet("YA_CONTRACTLINE_INS_PORC")                                                                      
									for n in range (contractline_insumos.count()):
										contractline_insumo = contractline_insumos.getMbo(n)
										if contractline_insumo is not None:
											insumo_porc = contractline_insumo.getString("YA_INSUMO")
											# Recorro cada moneda del insumo porcentual
											contractline_precios = contractline_insumo.getMboSet("YA_CONTRACTLINE_PRECIOS")
											if tipo == "PESOS":
												contractline_precios.setWhere(" ya_moneda = 'PESO' ")
											elif tipo == "OTRAS":
												contractline_precios.setWhere(" ya_moneda != 'PESO' ")
											contractline_precios.reset()                                                                                                                                                          
											for b in range (contractline_precios.count()):
												contractline_precio = contractline_precios.getMbo(b)
												if contractline_precio is not None:
													base_porc = contractline_precio.getDouble("YA_UNITCOST")
													moneda3 = contractline_precio.getString("YA_MONEDA")
													# Traigo todos los costos directos que tiene esa moneda
													costos_directos = contractline_precio.getMboSet("YA_PRECIOS_COSTOS_DIRECTOS")
													cd_total_unitario = 0
													cd_total_linea = 0
													cd_total_incremento = 0
													for q in range (costos_directos.count()):
														moneda = costos_directos.getMbo(q)   
														if moneda is not None:
															insumo_cd = moneda.getString("YA_INSUMO")
															rdp_objetivo = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
															rdp_objetivo.setWhere(" contractnum = '" + contrato3 + "' and revisionnum = '" + revision3 + "' and contractlinenum = '" + linea3 + "' and ya_insumo = '" + insumo_cd + "' and ya_moneda = '" + moneda3 + "' and ya_periodo = '" + periodo + "' and ya_clase = '" + clase + "' and ya_status = '" + estado_creacion + "' and ticketid = '" + ticket + "' ")                                                                                                                                  
															rdp_objetivo.reset()
															rdp_objetivo_linea = rdp_objetivo.getMbo(0)
															if rdp_objetivo_linea is not None:
																unitcost = rdp_objetivo_linea.getDouble("YA_UNITCOST_RDP")                       
																linecost = rdp_objetivo_linea.getDouble("YA_LINECOST_RDP")
																incremento_cd = rdp_objetivo_linea.getDouble("YA_INCREMENTO")                                                            
																cd_total_unitario = round(cd_total_unitario + unitcost,decimales)
																cd_total_linea = round(cd_total_linea + linecost,decimales)
																cd_total_incremento = round(cd_total_incremento + incremento_cd,decimales)
																
												# Busco los porcentajes de cada insumo porcentual
												insumo_contrato = contractline_insumo.getMboSet("YA_CONTRACT_INSUMOS").getMbo(0)
												if insumo_contrato is not None:
													porc_costo = insumo_contrato.getDouble("YA_PORC_CD")                                      
													
													# Calculo de redeterminacion
													subtotal_unitario = round(cd_total_unitario * porc_costo / 100,decimales)
													subtotal_linea = round(cd_total_linea * porc_costo / 100,decimales)
													
													# Calculo de incremento contractual
													subtotal_incremento = round(cd_total_incremento * porc_costo / 100,decimales)

													# Calculo de saldo
													# Traer cantidades de actas de mediciones anteriores
													strObject = "POLINE"
													strWhere =  "ponum in (select ponum from po where ya_tipo = 'FIS' and status = 'APROB' and YA_PERIODO < '" + periodo + "' ) and contreflineid in (select contractlineid from contractline where contractnum = '" + contrato3 + "' and contractlinenum = '" + linea3 + "')"
													actas_aprobadas_anteriores = mxServer.getMboSet(strObject, userInfo)
													actas_aprobadas_anteriores.setWhere(strWhere)
													actas_aprobadas_anteriores.reset()
													# Recorro cada AM y me traigo las cantidades
													cantidad_actas_aprobadas = 0
													for i in range (actas_aprobadas_anteriores.count()):
														acta_aprobada_anterior = actas_aprobadas_anteriores.getMbo(i)
														if acta_aprobada_anterior is not None:
															cantidad_acta = acta_aprobada_anterior.getDouble("ORDERQTY")
															# Defino la cantidad total
															cantidad_actas_aprobadas = round(cantidad_actas_aprobadas + cantidad_acta,decimales)
													# Defino el saldo de la linea
													saldo3 = round(cantidad3 - cantidad_actas_aprobadas,decimales)
													
													# Calculo de deltas para porcentuales
													delta_total3 = round(subtotal_incremento / (saldo3 * base_porc),decimales)
																						   
													# Calculo del costo saldo de obra
													costo_saldo_obra3 = round(subtotal_unitario * saldo3,decimales)                                     
													
													# Agrego registro a contractline_rdp
													redeterminaciones = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
													redeterminaciones.reset()
													redeterminaciones_add = redeterminaciones.add()
													redeterminaciones_add.setValue("CONTRACTNUM",contrato3)
													redeterminaciones_add.setValue("REVISIONNUM",revision3)
													redeterminaciones_add.setValue("CONTRACTLINENUM",linea3)
													redeterminaciones_add.setValue("YA_INSUMO",insumo_porc)
													redeterminaciones_add.setValue("YA_MONEDA",moneda3)
													redeterminaciones_add.setValue("YA_CLASE",clase)
													redeterminaciones_add.setValue("YA_PERIODO",periodo)
													redeterminaciones_add.setValue("TICKETID",ticket)
													redeterminaciones_add.setValue("YA_STATUS",estado_creacion)
													redeterminaciones_add.setValue("YA_FECHA_CALCULO",MXServer.getMXServer().getDate())
													redeterminaciones_add.setValue("YA_UNITCOST_RDP",subtotal_unitario)
													redeterminaciones_add.setValue("YA_LINECOST_RDP",subtotal_linea)
													redeterminaciones_add.setValue("YA_DELTA_RDP",subtotal_unitario/base_porc)                                       
													redeterminaciones_add.setValue("YA_SALDO",saldo3)
													redeterminaciones_add.setValue("YA_INCREMENTO",subtotal_incremento)
													redeterminaciones_add.setValue("YA_DELTA_AJUSTE",delta_total3)
													redeterminaciones_add.setValue("YA_COSTO_SALDO_OBRA",costo_saldo_obra3)
													redeterminaciones.save()                                                                       


																  
							# Valido que haya la misma cantidad de lineas de contractline_precios que de contractline_rdp generadas (por TIPO)
							
							# 1- Traigo todas las lineas de contractline_rdp que genere
							contractline_rdp_generadas = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
							contractline_rdp_generadas.setWhere(" ticketid = '" + ticket + "' and ya_status = '" + estado_creacion + "' ")
							contractline_rdp_generadas.reset()                          
							
							# 2- Cuento cantidad de lineas contractline_precios del contrato
							contractline_precios_comp = mbo.getMboSet("YA_CONTRACTLINE_PRECIOS")
							if tipo == "PESOS":
								contractline_precios_comp.setWhere(" ya_moneda = 'PESO' ")
							elif tipo == "OTRAS":
								contractline_precios_comp.setWhere(" ya_moneda != 'PESO' ")
							contractline_precios_comp.reset()
							cantidad_lineas_precio = contractline_precios_comp.count()
							
							# 3- Cuento cantidad de contractline_rdp generadas
							cantidad_lineas_rdp = contractline_rdp_generadas.count()							
							
							#setError(str(cantidad_lineas_precio)+"-"+str(cantidad_lineas_rdp))
							
							# 4- Hago la comparacion
							if cantidad_lineas_precio != cantidad_lineas_rdp:
								error = 1
								setError("Faltan definir niveles de ajuste para el calculo de la redeterminacion. Agregarlos y volver a calcular la rdp")
							
							
							# Si tengo algun error (error = 1) desestimo todo lo que genere
							if error == 1:                   
								contractline_rdp_generadas = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
								contractline_rdp_generadas.setWhere(" ticketid = '" + ticket + "' ")
								contractline_rdp_generadas.reset()                    
								for f in range (contractline_rdp_generadas.count()):
									linea_generada = contractline_rdp_generadas.getMbo(f)
									if linea_generada is not None:
										linea_generada.setValue("YA_STATUS","DESESTIMADO")
										contractline_rdp_generadas.save()              
							
							
							"""Calculo de incremento y variacion contractual para moneda PESO"""
							if tipo == "PESOS":
								# Traigo todas las contractline_rdp que se generaron
								strObject = "CONTRACTLINE_RDP"                         
								strWhere =  " ticketid = '" + ticket + "' and ya_status = '" + estado_creacion + "' "
								contractline_rdp_generadas = mxServer.getMboSet(strObject, userInfo)
								contractline_rdp_generadas.setWhere(strWhere)
								contractline_rdp_generadas.reset()
								
								incremento_contractual = 0
								saldo_obra = 0
								if contractline_rdp_generadas.count() > 0:
									for b in range (contractline_rdp_generadas.count()):
										contractline_rdp_generada = contractline_rdp_generadas.getMbo(b)
										if contractline_rdp_generada is not None:
											incremento_i = contractline_rdp_generada.getDouble("YA_INCREMENTO")
											incremento_contractual = round(incremento_contractual + incremento_i,decimales)
											saldo_obra_i = contractline_rdp_generada.getDouble("YA_COSTO_SALDO_OBRA")
											saldo_obra = round(saldo_obra + saldo_obra_i,decimales)
									
									variacion = round((incremento_contractual / (saldo_obra-incremento_contractual))*100,decimales)        
									if v==0:
										ticket_rdp.setValue("YA_VAL_INCREMENTO_CONTRACTUAL",incremento_contractual)
										ticket_rdp.setValue("YA_VAL_COSTO_SALDO_OBRA",saldo_obra)                           
										ticket_rdp.setValue("YA_VAL_VARIACION",variacion)                       
									elif v==1:
										ticket_rdp.setValue("YA_INCREMENTO_CONTRACTUAL",incremento_contractual)
										ticket_rdp.setValue("YA_COSTO_SALDO_OBRA",saldo_obra)                           
										ticket_rdp.setValue("YA_VARIACION",variacion)
									if clase == "VALIDACION":
										# Validacion
										if variacion < 4:
											var_menor_4 = 1
											# Rechazo de redeterminaciones por linea
											for p in range (contractline_rdp_generadas.count()):
												contractline_rdp_generada = contractline_rdp_generadas.getMbo(p)
												if contractline_rdp_generada is not None:                                            
													contractline_rdp_generada.setValue("YA_STATUS","RECHAZADO")
													contractline_rdp_generada.setValue("YA_CLASE","VALIDACION")
											contractline_rdp_generadas.save()
											# Rechazo de solicitud de redeterminacion
											ticket_rdp.changeStatus("RDP_RECH", MXServer.getMXServer().getDate(), 'RDP rechazada por variacion menor al 4%')
											errorkey='variacion_contractual'
											errorgroup='rdp'
											ticket_rdp.setValue("YA_REDETERMINAR",0)
											lista_ticket_rdp.save()
					
					if error == 0:
						# Saco check
						ticket_rdp.setValue("YA_REDETERMINAR",0)
						
						# Cambio de estado el ticket a PNDREV_RDP
						estado_ticket = ticket_rdp.getString("STATUS")
						if estado_ticket not in ["PNDREV_RDP","RDP_RECH"]:
							ticket_rdp.changeStatus("PNDREV_RDP", MXServer.getMXServer().getDate(), 'RDP calculada')                                                
						
						# Cambio de estado el contrato a PNDREV_RDP
						#estado = mbo.getString("STATUS")
						#if estado != "PNDREV_RDP":
							#mbo.changeStatus("PNDREV_RDP", MXServer.getMXServer().getDate(), 'RDP calculada')
							
						# Guardar cambios    
						ticket_rdp.getThisMboSet().save()
						mbo.getThisMboSet().save()
						
						# Aviso de Ajuste Exitoso
						setWarn("El Ajuste/RDP fue calculado de forma exitosa. Para visualizarlos, ingresar a la solapa ""Items del Contrato"" y cada item tendra asociado su ajuste en la seccion inferior de la pantalla")
							
								
		# Elimino registros de contractline_rdp que tengan estado DESESTIMADO (por error o porque se realizo una nueva redeterminacion)
		con = mxServer.getDBManager().getConnection(conKey)
		sql = con.createStatement()
		rs = sql.executeQuery("delete from contractline_rdp where ya_status = 'DESESTIMADO' and contractnum = '" + n_contrato + "' ")
		con.commit()
		mxServer.getDBManager().freeConnection(conKey)



# ESCALAMIENTO DE VALIDACION

if launchPoint == "YA_RDP_VALID":
	
	# Setear las variables globales
	mxServer = MXServer.getMXServer()
	userInfo = mbo.getUserInfo()
	conKey = userInfo.getConnectionKey()

	# Variables generales
	ticket = str(SimpleDateFormat("YYMMddHHmm").format(MXServer.getMXServer().getDate()))
	avanzado = mbo.getBoolean("YA_CONTRATO_AVANZADO")
	status_contrato = mbo.getString("STATUS")
	n_contrato = mbo.getString("CONTRACTNUM")
	rev_contrato = mbo.getString("REVISIONNUM")
	periodo_actual = str(SimpleDateFormat("YYYYMM").format(MXServer.getMXServer().getDate()))
	mes = str(SimpleDateFormat("MM").format(MXServer.getMXServer().getDate()))
	periodo = str(int(SimpleDateFormat("YYYYMM").format(MXServer.getMXServer().getDate())))
	"""
	if mes != "01":
		periodo = str(int(SimpleDateFormat("YYYYMM").format(MXServer.getMXServer().getDate()))-1)
	if mes == "01":
		periodo = str(int(SimpleDateFormat("YYYYMM").format(MXServer.getMXServer().getDate()))-89)
	"""
	
	"""PESOS Y OTRAS MONEDAS"""
	# Veo si tiene el acta de medicion cargada para ese mes (mes anterior al actual)
	acta_correspondiente = MXServer.getMXServer().getMboSet("PO", MXServer.getMXServer().getSystemUserInfo());
	acta_correspondiente.setWhere(" ya_tipo = 'FIS' and ponum like '%AM%' and CONTRACTREFNUM = '"+n_contrato+"' and STATUS = 'APROB' and YA_PERIODO = '"+periodo+"' ")
	acta_correspondiente.reset()	
	if acta_correspondiente.count() == 1:
		acta_aprobada = 1
	else:
		acta_aprobada = 0
		
	"""OTRAS MONEDAS"""
	# Calculo cantidad de indices cargados a la polinomica para OTRAS MONEDAS
	indices_utilizados_otras = MXServer.getMXServer().getMboSet("CONTRACT_POLINOMICA", MXServer.getMXServer().getSystemUserInfo());
	indices_utilizados_otras.setWhere(" contractnum = '"+n_contrato+"' and revisionnum = '"+rev_contrato+"' and ya_moneda != 'PESO' ")
	indices_utilizados_otras.reset()
	lista_indices_otras = []
	for i in range (indices_utilizados_otras.count()):
		indice_otras = indices_utilizados_otras.getMbo(i)
		if indice_otras is not None:
			ya_indice_otras = indice_otras.getString("YA_INDICE")
			if ya_indice_otras not in lista_indices_otras:
				lista_indices_otras.append(ya_indice_otras)
	# Chequeo que tengan registros para ese periodo
	esta_cargado_otras = 1
	for m in lista_indices_otras:
		if esta_cargado_otras == 1:
			indices_valores_otras = MXServer.getMXServer().getMboSet("INDICES_VALORES", MXServer.getMXServer().getSystemUserInfo());
			indices_valores_otras.setWhere(" ya_indice = '"+m+"' and status = 'PUBLICADO' and ya_per_indice = '"+periodo+"' ")
			indices_valores_otras.reset()
			if indices_valores_otras.count() == 1:
				esta_cargado_otras = 1
			else:
				esta_cargado_otras = 0
	
	# Chequeo de si mando el mail
	mails_mismo_periodo_otras = MXServer.getMXServer().getMboSet("COMMLOG", MXServer.getMXServer().getSystemUserInfo());
	mails_mismo_periodo_otras.setWhere(" OWNERTABLE = 'CONTRACT' AND SUBJECT LIKE '%Otras%' AND replace(to_char(createdate,'YYYY-MM'),'-') = '" + periodo_actual + "' ")
	mails_mismo_periodo_otras.reset()


	# Toma de decision OTRAS MONEDAS
	if esta_cargado_otras == 1 and acta_aprobada == 1 and mails_mismo_periodo_otras.count() == 0:
		# Envio mail avisando que esta listo para pedir la rdp
		commTpltSet = MXServer.getMXServer().getMboSet("COMMTEMPLATE",MXServer.getMXServer().getSystemUserInfo())
		commTpltSet.setWhere("templateid='YA_OTRAS_OK'")
		commTpltSet.reset()
		commTpltSet.getMbo(0).sendMessage(mbo, mbo)
	else:
		pass
	
	
	"""PESOS"""
	# Calculo cantidad de indices cargados a la polinomica para PESOS
	indices_utilizados = MXServer.getMXServer().getMboSet("CONTRACT_POLINOMICA", MXServer.getMXServer().getSystemUserInfo());
	indices_utilizados.setWhere(" contractnum = '"+n_contrato+"' and revisionnum = '"+rev_contrato+"' and ya_moneda = 'PESO' ")
	indices_utilizados.reset()
	lista_indices = []
	for i in range (indices_utilizados.count()):
		indice = indices_utilizados.getMbo(i)
		if indice is not None:
			ya_indice = indice.getString("YA_INDICE")
			if ya_indice not in lista_indices:
				lista_indices.append(ya_indice)
	# Chequeo que tengan registros para ese periodo		
	esta_cargado = 1
	for j in lista_indices:
		if esta_cargado == 1:
			indices_valores = MXServer.getMXServer().getMboSet("INDICES_VALORES", MXServer.getMXServer().getSystemUserInfo());
			indices_valores.setWhere(" ya_indice = '"+j+"' and status = 'PUBLICADO' and ya_per_indice = '"+periodo+"' ")
			indices_valores.reset()
			if indices_valores.count() == 1:
				esta_cargado = 1
			else:
				esta_cargado = 0		

	# Chequeo de si mando el mail
	mails_mismo_periodo = MXServer.getMXServer().getMboSet("COMMLOG", MXServer.getMXServer().getSystemUserInfo());
	mails_mismo_periodo.setWhere(" OWNERTABLE = 'CONTRACT' AND SUBJECT LIKE '%Pesos%' AND replace(to_char(createdate,'YYYY-MM'),'-') = '" + periodo_actual + "' ")
	mails_mismo_periodo.reset()
	
	# Toma de decision PESOS
	if esta_cargado == 1 and acta_aprobada == 1 and mails_mismo_periodo.count() == 0:
		# Valido el 4%
		def setError(texto):
			global errorkey, errorgroup, params
			errorkey='rdp'
			errorgroup='contract'
			params=[texto]
		# Seteo en 0 el error (error = 0 -> no hay errores)
		error = 0
		# Cantidad de decimales a redondear
		decimales = 4
		# Traigo el periodo, clase y tipo
		tipo = "PESOS"
		# Traigo periodo base del contrato
		periodo_base = mbo.getString("YA_PER_INDICE")                
		
		# Defino variable para saber si tengo que volver a correr el calculo por variacion del 4%
		var_menor_4 = 0		
		if tipo == "PESOS":
			x = 1
			validacion = 1                  
		else:
			x = 1
			validacion = 0
			estado_creacion = "INGRESADO"				
		for v in range (x):   
			if var_menor_4 == 0:
									
				if v == 0 and validacion == 1:
					nivel_ajuste = mbo.getString("YA_CLAVE_RDP_PROV")
					clase = "PRE_VALIDACION"
					estado_creacion = "VAL_INGRESADO"
				elif v == 1 and validacion == 1:
					estado_creacion = "INGRESADO"
				
				# Redeterminacion tipo PESOS                
				if tipo == "PESOS":
					
					# Generales
									   
					# Redeterminacion DEFINITIVA                   
					if clase == "DEF":
						nivel_ajuste = mbo.getString("YA_CLAVE_RDP")
						
					# Redeterminacion PROVISORIA
					if clase == "PROV":
						nivel_ajuste = mbo.getString("YA_CLAVE_RDP_PROV")
						
					# RDP 1
					if nivel_ajuste == "1":
						combinaciones = mbo.getMboSet("YA_CLAVE_PESO1")
					# RDP 2
					if nivel_ajuste == "2":
						combinaciones = mbo.getMboSet("YA_CLAVE_PESO2")
					# RDP i
					
				   
				# Redeterminacion tipo OTRAS
				elif tipo == "OTRAS":           
					
					# Redeterminacion DEFINITIVA                   
					if clase == "DEF":     
						nivel_ajuste = mbo.getString("YA_CLAVE_RDP")
					
					# RDP 1
					if nivel_ajuste == "1":
						combinaciones = mbo.getMboSet("YA_CLAVE_NOPESO1")
					# RDP 2
					elif nivel_ajuste == "2":
						combinaciones = mbo.getMboSet("YA_CLAVE_NOPESO2")                    
					# RDP i 
					
				for z in range (combinaciones.count()):
					combinacion = combinaciones.getMbo(z)
					if combinacion is not None:    
						# Atributos Generales (aplica a todos los niveles de ajuste)
						contrato = combinacion.getString("CONTRACTNUM")
						revision = combinacion.getString("REVISIONNUM")
						moneda = combinacion.getString("YA_MONEDA")                       
						# Atributos RDP 1
						jerarquia = combinacion.getString("CLASSSTRUCTUREID")
						insumo = combinacion.getString("YA_INSUMO")        
						# Atributos RDP 2                       
						# Atributos RDP i
						
						
						# Variables Generales (aplica a todos los niveles de ajuste)
						lineas_contrato = mbo.getMboSet("CONTRACTLINE")                       
						
						# Variables RDP 1     
						if nivel_ajuste == "1":                    
							# Indices
							indices = combinacion.getMboSet("YA_POLINOMICA")
							# Lineas a la que se aplica la rdp
							lineas_precio = MXServer.getMXServer().getMboSet("contractline_precios", MXServer.getMXServer().getSystemUserInfo());
							lineas_precio.setWhere(" ya_insumo = '" + insumo + "' and ya_moneda = '" + moneda + "' and revisionnum = '" + revision + "' and contractnum = '" + contrato + "' and ya_insumo in (select ya_insumo from contract_insumos where contractnum = '" + contrato + "' and revisionnum = '" + revision + "' and ya_tipo_costo != '%CD') and contractlinenum in (select contractline.contractlinenum from contractline inner join contractline_precios on contractline.contractnum = contractline_precios.contractnum and contractline.revisionnum = contractline_precios.revisionnum and contractline.contractlinenum = contractline_precios.contractlinenum where contractline.contractlinenum in (select contractline.contractlinenum from classancestor inner join contractline on contractline.classstructureid = classancestor.classstructureid where ancestor = '" + jerarquia + "'))")
							lineas_precio.reset()                            
						
						# Variables RDP 2
						elif nivel_ajuste == "2":
							# Indices
							indices = combinacion.getMboSet("YA_POLINOMICA2")
							# Lineas a la que se aplica la rdp
							lineas_precio = MXServer.getMXServer().getMboSet("contractline_precios", MXServer.getMXServer().getSystemUserInfo());
							lineas_precio.setWhere(" ya_moneda = '" + moneda + "' and revisionnum = '" + revision + "' and contractnum = '" + contrato + "' and ya_insumo in (select ya_insumo from contract_insumos where contractnum = '" + contrato + "' and revisionnum = '" + revision + "' and ya_tipo_costo != '%CD') ")
							lineas_precio.reset()

						# Variables RDP i
						# Definir variable "indices" y variable "lineas_precio" (relacion ya_polinomicai y setWhere para contractline_precios) segun este definido el nivel de ajuste
							
						# Calculo de polinomica    
						resultado_polinomica = 0
						for y in range (indices.count()):
							indice = indices.getMbo(y)
							if indice is not None:
								indice1 = indice.getString("YA_INDICE")
								porc_incid = indice.getDouble("YA_PORC_INCIDENCIA")
								# Traigo los valores de los indices en el periodo del ticket
								valores = MXServer.getMXServer().getMboSet("INDICES_VALORES", MXServer.getMXServer().getSystemUserInfo());
								valores.setWhere(" ya_indice = '" + indice1 + "' and YA_PER_INDICE = '" + periodo + "' and status = 'PUBLICADO' ")
								valores.reset()
								valor = valores.getMbo(0)
								if valor is not None:
									valor_indice = valor.getDouble("YA_VALOR_INDICE")
									valores.save()
									# Traigo los valores de los indices en el periodo base
									valores_base = MXServer.getMXServer().getMboSet("INDICES_VALORES", MXServer.getMXServer().getSystemUserInfo());
									valores_base.setWhere(" ya_indice = '" + indice1 + "' and YA_PER_INDICE = '" + periodo_base + "' and status = 'PUBLICADO' ")
									valores_base.reset()
									valor_base = valores_base.getMbo(0)
									if valor_base is not None:
										valor_indice_base = valor_base.getDouble("YA_VALOR_INDICE")
										valores_base.save()
										# Calculo cada termino de la polinomica (cada indice)
										resultado_indice = round((porc_incid / 100) * valor_indice / valor_indice_base,decimales)
										# Calculo la polinomica (suma de cada indice)
										resultado_polinomica = round(resultado_polinomica + resultado_indice,decimales)                         
								else:
									error = 1                                     
									setError("El indice " + indice1 + " no tiene cargado el valor para el periodo de la solicitud. Por favor cargue ese valor y vuelva a calcular la redeterminacion." )
						if indices.count() == 0:
								error = 1                                     
								setError("Existe un nivel de ajuste sin indices cargados. Por favor cargue los indices que falten y vuelva a realizar el calculo." )                                               
					
							
						# Calculo de redeterminacion para costos directos                    
						for f in range (lineas_precio.count()):
							precio = lineas_precio.getMbo(f)
							if precio is not None:
								# Traigo cantidad de la linea
								linea = precio.getMboSet("YA_CONTRACTLINE").getMbo(0)
								if linea is not None:
									cantidad = linea.getDouble("ORDERQTY")                                
									precio_actual = precio.getDouble("YA_UNITCOST")
									# Calculo el precio unitario de redeterminacion
									precio_redeterminado = round(precio_actual * resultado_polinomica,decimales)
									# Calculo el precio de linea de redeterminacion
									precio_redeterminado_linea = round(precio_redeterminado * cantidad,decimales)
									# Traigo atributos de contractline_precios
									linea = precio.getString("CONTRACTLINENUM")
									insumo2 = precio.getString("YA_INSUMO")
									
									# Calculo de saldos
									# Traer cantidades de actas de mediciones anteriores
									strObject = "POLINE"
									strWhere =  "ponum in (select ponum from po where ya_tipo = 'FIS' and status = 'APROB' and YA_PERIODO < '" + periodo + "' ) and contreflineid in (select contractlineid from contractline where contractnum = '" + contrato + "' and contractlinenum = '" + linea + "')"
									actas_aprobadas_anteriores = mxServer.getMboSet(strObject, userInfo)
									actas_aprobadas_anteriores.setWhere(strWhere)
									actas_aprobadas_anteriores.reset()
									# Recorro cada AM y me traigo las cantidades
									cantidad_actas_aprobadas = 0
									for i in range (actas_aprobadas_anteriores.count()):
										acta_aprobada_anterior = actas_aprobadas_anteriores.getMbo(i)
										if acta_aprobada_anterior is not None:
											cantidad_acta = acta_aprobada_anterior.getDouble("ORDERQTY")
											# Defino la cantidad total
											cantidad_actas_aprobadas = round(cantidad_actas_aprobadas + cantidad_acta,decimales)
									# Defino el saldo de la linea
									saldo = round(cantidad - cantidad_actas_aprobadas,decimales)

									# Calculo de deltas para costos directos
									# Traer contractline_rdp anteriores de cada linea (por insumo y moneda)
									strObject = "CONTRACTLINE_RDP"
									if v == 0 and validacion == 1:
										strWhere =  "contractnum = '" + contrato + "' and revisionnum = '" + revision + "' and contractlinenum = '" + linea + "' and ya_insumo = '" + insumo2 + "' and ya_moneda = '" + moneda + "' and ya_periodo < '" + periodo + "' and ya_status = 'VAL_INGRESADO' and ya_clase = 'PRE_VALIDACION' and ticketid != '" + ticket + "' "
									elif (v == 1 and validacion == 1) or (validacion == 0):                                              
										strWhere =  "contractnum = '" + contrato + "' and revisionnum = '" + revision + "' and contractlinenum = '" + linea + "' and ya_insumo = '" + insumo2 + "' and ya_moneda = '" + moneda + "' and ya_periodo <= '" + periodo + "' and ya_status = 'APROB' and ya_clase in ('PROV','DEF') and ticketid != '" + ticket + "' "
									rdps_aprobadas_anteriores = mxServer.getMboSet(strObject, userInfo)
									rdps_aprobadas_anteriores.setWhere(strWhere)
									rdps_aprobadas_anteriores.reset()
									
									# Recorro cada RDP y me traigo el valor del DELTA
									deltas_anteriores = 0
									
									periodos_tomados = []
									
									for j in range (rdps_aprobadas_anteriores.count()):
										rdp_aprobada_anterior = rdps_aprobadas_anteriores.getMbo(j)
										if rdp_aprobada_anterior is not None:                                           
											delta = rdp_aprobada_anterior.getDouble("YA_DELTA_AJUSTE")
											# Defino la suma de los deltas anteriores
											deltas_anteriores = round(deltas_anteriores + delta,decimales)
									# Defino el delta total (El 1 corresponde al "DELTA" base)
									delta_total = round(resultado_polinomica - deltas_anteriores - 1,decimales)                                      

									# Calculo del incremento contractual
									incremento = round(saldo * delta_total * precio_actual,decimales)
									
									# Calculo del costo saldo de obra
									costo_saldo_obra = round(precio_redeterminado * saldo,decimales)
									
									# Agrego registro a contractline_rdp
									redeterminaciones = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
									redeterminaciones.reset()
									redeterminaciones_add = redeterminaciones.add()
									redeterminaciones_add.setValue("CONTRACTNUM",contrato)
									redeterminaciones_add.setValue("REVISIONNUM",revision)
									redeterminaciones_add.setValue("CONTRACTLINENUM",linea)
									redeterminaciones_add.setValue("YA_INSUMO",insumo2)
									redeterminaciones_add.setValue("YA_MONEDA",moneda)
									redeterminaciones_add.setValue("YA_CLASE",clase)
									redeterminaciones_add.setValue("YA_PERIODO",periodo)
									redeterminaciones_add.setValue("TICKETID",ticket)
									redeterminaciones_add.setValue("YA_STATUS",estado_creacion)
									redeterminaciones_add.setValue("YA_FECHA_CALCULO",MXServer.getMXServer().getDate())
									redeterminaciones_add.setValue("YA_UNITCOST_RDP",precio_redeterminado)
									redeterminaciones_add.setValue("YA_LINECOST_RDP",precio_redeterminado_linea)
									redeterminaciones_add.setValue("YA_DELTA_RDP",resultado_polinomica)
									redeterminaciones_add.setValue("YA_DELTA_AJUSTE",delta_total)
									redeterminaciones_add.setValue("YA_SALDO",saldo)
									redeterminaciones_add.setValue("YA_INCREMENTO",incremento)
									redeterminaciones_add.setValue("YA_COSTO_SALDO_OBRA",costo_saldo_obra)
									redeterminaciones.save()                                     
										   
				
				# Recalculo de insumos porcentuales
				# Recorro cada linea
				
				for g in range (lineas_contrato.count()):
					lineas = lineas_contrato.getMbo(g)
					if lineas is not None:
						linea3 = lineas.getString("CONTRACTLINENUM")
						contrato3 = lineas.getString("CONTRACTNUM")
						revision3 = lineas.getString("REVISIONNUM")
						cantidad3 = lineas.getDouble("ORDERQTY")
						# Recorro cada insumo porcentual
						contractline_insumos = lineas.getMboSet("YA_CONTRACTLINE_INS_PORC")                                                                      
						for n in range (contractline_insumos.count()):
							contractline_insumo = contractline_insumos.getMbo(n)
							if contractline_insumo is not None:
								insumo_porc = contractline_insumo.getString("YA_INSUMO")
								# Recorro cada moneda del insumo porcentual
								contractline_precios = contractline_insumo.getMboSet("YA_CONTRACTLINE_PRECIOS")
								if tipo == "PESOS":
									contractline_precios.setWhere(" ya_moneda = 'PESO' ")
								elif tipo == "OTRAS":
									contractline_precios.setWhere(" ya_moneda != 'PESO' ")
								contractline_precios.reset()                                                                                                                                                          
								for b in range (contractline_precios.count()):
									contractline_precio = contractline_precios.getMbo(b)
									if contractline_precio is not None:
										base_porc = contractline_precio.getDouble("YA_UNITCOST")
										moneda3 = contractline_precio.getString("YA_MONEDA")
										# Traigo todos los costos directos que tiene esa moneda
										costos_directos = contractline_precio.getMboSet("YA_PRECIOS_COSTOS_DIRECTOS")
										cd_total_unitario = 0
										cd_total_linea = 0
										cd_total_incremento = 0
										for q in range (costos_directos.count()):
											moneda = costos_directos.getMbo(q)   
											if moneda is not None:
												insumo_cd = moneda.getString("YA_INSUMO")
												rdp_objetivo = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
												rdp_objetivo.setWhere(" contractnum = '" + contrato3 + "' and revisionnum = '" + revision3 + "' and contractlinenum = '" + linea3 + "' and ya_insumo = '" + insumo_cd + "' and ya_moneda = '" + moneda3 + "' and ya_periodo = '" + periodo + "' and ya_clase = '" + clase + "' and ya_status = '" + estado_creacion + "' and ticketid = '" + ticket + "' ")                                                                                                                                  
												rdp_objetivo.reset()
												rdp_objetivo_linea = rdp_objetivo.getMbo(0)
												if rdp_objetivo_linea is not None:
													unitcost = rdp_objetivo_linea.getDouble("YA_UNITCOST_RDP")                       
													linecost = rdp_objetivo_linea.getDouble("YA_LINECOST_RDP")
													incremento_cd = rdp_objetivo_linea.getDouble("YA_INCREMENTO")                                                            
													cd_total_unitario = round(cd_total_unitario + unitcost,decimales)
													cd_total_linea = round(cd_total_linea + linecost,decimales)
													cd_total_incremento = round(cd_total_incremento + incremento_cd,decimales)
													
									# Busco los porcentajes de cada insumo porcentual
									insumo_contrato = contractline_insumo.getMboSet("YA_CONTRACT_INSUMOS").getMbo(0)
									if insumo_contrato is not None:
										porc_costo = insumo_contrato.getDouble("YA_PORC_CD")                                      
										
										# Calculo de redeterminacion
										subtotal_unitario = round(cd_total_unitario * porc_costo / 100,decimales)
										subtotal_linea = round(cd_total_linea * porc_costo / 100,decimales)
										
										# Calculo de incremento contractual
										subtotal_incremento = round(cd_total_incremento * porc_costo / 100,decimales)

										# Calculo de saldo
										# Traer cantidades de actas de mediciones anteriores
										strObject = "POLINE"
										strWhere =  "ponum in (select ponum from po where ya_tipo = 'FIS' and status = 'APROB' and YA_PERIODO < '" + periodo + "' ) and contreflineid in (select contractlineid from contractline where contractnum = '" + contrato3 + "' and contractlinenum = '" + linea3 + "')"
										actas_aprobadas_anteriores = mxServer.getMboSet(strObject, userInfo)
										actas_aprobadas_anteriores.setWhere(strWhere)
										actas_aprobadas_anteriores.reset()
										# Recorro cada AM y me traigo las cantidades
										cantidad_actas_aprobadas = 0
										for i in range (actas_aprobadas_anteriores.count()):
											acta_aprobada_anterior = actas_aprobadas_anteriores.getMbo(i)
											if acta_aprobada_anterior is not None:
												cantidad_acta = acta_aprobada_anterior.getDouble("ORDERQTY")
												# Defino la cantidad total
												cantidad_actas_aprobadas = round(cantidad_actas_aprobadas + cantidad_acta,decimales)
										# Defino el saldo de la linea
										saldo3 = round(cantidad3 - cantidad_actas_aprobadas,decimales)
										
										# Calculo de deltas para porcentuales
										delta_total3 = round(subtotal_incremento / (saldo3 * base_porc),decimales)
																			   
										# Calculo del costo saldo de obra
										costo_saldo_obra3 = round(subtotal_unitario * saldo3,decimales)                                     
										
										# Agrego registro a contractline_rdp
										redeterminaciones = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
										redeterminaciones.reset()
										redeterminaciones_add = redeterminaciones.add()
										redeterminaciones_add.setValue("CONTRACTNUM",contrato3)
										redeterminaciones_add.setValue("REVISIONNUM",revision3)
										redeterminaciones_add.setValue("CONTRACTLINENUM",linea3)
										redeterminaciones_add.setValue("YA_INSUMO",insumo_porc)
										redeterminaciones_add.setValue("YA_MONEDA",moneda3)
										redeterminaciones_add.setValue("YA_CLASE",clase)
										redeterminaciones_add.setValue("YA_PERIODO",periodo)
										redeterminaciones_add.setValue("TICKETID",ticket)
										redeterminaciones_add.setValue("YA_STATUS",estado_creacion)
										redeterminaciones_add.setValue("YA_FECHA_CALCULO",MXServer.getMXServer().getDate())
										redeterminaciones_add.setValue("YA_UNITCOST_RDP",subtotal_unitario)
										redeterminaciones_add.setValue("YA_LINECOST_RDP",subtotal_linea)
										redeterminaciones_add.setValue("YA_DELTA_RDP",subtotal_unitario/base_porc)                                       
										redeterminaciones_add.setValue("YA_SALDO",saldo3)
										redeterminaciones_add.setValue("YA_INCREMENTO",subtotal_incremento)
										redeterminaciones_add.setValue("YA_DELTA_AJUSTE",delta_total3)
										redeterminaciones_add.setValue("YA_COSTO_SALDO_OBRA",costo_saldo_obra3)
										redeterminaciones.save()                                                                       


													  
				# Valido que haya la misma cantidad de lineas de contractline_precios que de contractline_rdp generadas (por TIPO)
				
				# 1- Traigo todas las lineas de contractline_rdp que genere
				contractline_rdp_generadas = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
				contractline_rdp_generadas.setWhere(" ticketid = '" + ticket + "' and ya_status = '" + estado_creacion + "' ")
				contractline_rdp_generadas.reset()                          
				
				# 2- Cuento cantidad de lineas contractline_precios del contrato
				contractline_precios_comp = mbo.getMboSet("YA_CONTRACTLINE_PRECIOS")
				if tipo == "PESOS":
					contractline_precios_comp.setWhere(" ya_moneda = 'PESO' ")
				elif tipo == "OTRAS":
					contractline_precios_comp.setWhere(" ya_moneda != 'PESO' ")
				contractline_precios_comp.reset()
				cantidad_lineas_precio = contractline_precios_comp.count()
				
				# 3- Cuento cantidad de contractline_rdp generadas
				cantidad_lineas_rdp = contractline_rdp_generadas.count()
				
				# 4- Hago la comparacion
				if cantidad_lineas_precio != cantidad_lineas_rdp:
					error = 1
					setError("Faltan definir niveles de ajuste para el calculo de la redeterminacion. Agregarlos y volver a calcular la rdp")
				
				
				# Si tengo algun error (error = 1) desestimo todo lo que genere
				if error == 1:                   
					contractline_rdp_generadas = MXServer.getMXServer().getMboSet("CONTRACTLINE_RDP", MXServer.getMXServer().getSystemUserInfo());
					contractline_rdp_generadas.setWhere(" ticketid = '" + ticket + "' ")
					contractline_rdp_generadas.reset()                    
					for f in range (contractline_rdp_generadas.count()):
						linea_generada = contractline_rdp_generadas.getMbo(f)
						if linea_generada is not None:
							linea_generada.setValue("YA_STATUS","DESESTIMADO")
							contractline_rdp_generadas.save()              
				
				
				"""Calculo de incremento y variacion contractual para moneda PESO"""
				if tipo == "PESOS":
					# Traigo todas las contractline_rdp que se generaron
					strObject = "CONTRACTLINE_RDP"                         
					strWhere =  " ticketid = '" + ticket + "' and ya_status = '" + estado_creacion + "' "
					contractline_rdp_generadas = mxServer.getMboSet(strObject, userInfo)
					contractline_rdp_generadas.setWhere(strWhere)
					contractline_rdp_generadas.reset()                    
					incremento_contractual = 0
					saldo_obra = 0
					for b in range (contractline_rdp_generadas.count()):
						contractline_rdp_generada = contractline_rdp_generadas.getMbo(b)
						if contractline_rdp_generada is not None:
							incremento_i = contractline_rdp_generada.getDouble("YA_INCREMENTO")
							incremento_contractual = round(incremento_contractual + incremento_i,decimales)
							saldo_obra_i = contractline_rdp_generada.getDouble("YA_COSTO_SALDO_OBRA")
							saldo_obra = round(saldo_obra + saldo_obra_i,decimales)
					variacion = round((incremento_contractual / (saldo_obra-incremento_contractual))*100,decimales)        
					if clase == "PRE_VALIDACION":
						# Validacion
						if variacion < 4:
							var_menor_4 = 1
							# Rechazo de redeterminaciones por linea
							for p in range (contractline_rdp_generadas.count()):
								contractline_rdp_generada = contractline_rdp_generadas.getMbo(p)
								if contractline_rdp_generada is not None:                                            
									contractline_rdp_generada.setValue("YA_STATUS","RECHAZADO")
									contractline_rdp_generada.setValue("YA_CLASE","PRE_VALIDACION")
							contractline_rdp_generadas.save()
							# Envio mail avisando que no alcanzo el 4%
							commTpltSet = MXServer.getMXServer().getMboSet("COMMTEMPLATE",MXServer.getMXServer().getSystemUserInfo())
							commTpltSet.setWhere("templateid='YA_PESO_NOVAL4'")
							commTpltSet.reset()
							commTpltSet.getMbo(0).sendMessage(mbo, mbo)
						elif variacion >= 4:
							var_menor_4 = 1
							# Envio mail avisando que supero el 4%
							commTpltSet = MXServer.getMXServer().getMboSet("COMMTEMPLATE",MXServer.getMXServer().getSystemUserInfo())
							commTpltSet.setWhere("templateid='YA_PESO_VAL4'")
							commTpltSet.reset()
							commTpltSet.getMbo(0).sendMessage(mbo, mbo)											

								
		# Elimino registros de contractline_rdp que tengan estado DESESTIMADO (por error o porque se realizo una nueva redeterminacion)
		con = mxServer.getDBManager().getConnection(conKey)
		sql = con.createStatement()
		rs = sql.executeQuery("delete from contractline_rdp where ya_status = 'DESESTIMADO' and contractnum = '" + n_contrato + "' ")
		con.commit()
		mxServer.getDBManager().freeConnection(conKey)

	else:
		pass


  
	# Por cada nuevo nivel de ajuste que se agregue, tener en cuenta:
		# Agregar el nivel al dominio YA_CLAVE_RDP para que pueda ser seleccionada en el contrato
		# Agregar el atributo en las tablas correspondientes
		# Modificar el indice de la tabla CONTRACT_CLAVE_RDP agregando este nuevo atributo (se tiene que borrar el indice y volver a generarlo)
		# Crear una nueva pestaña de configuracion en la app ya_contpurch
		# Modificar este script (YA_RDP) buscar comentarios de tipo "RDP i"