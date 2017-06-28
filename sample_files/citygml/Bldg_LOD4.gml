<?xml version="1.0" encoding="utf-8"?>
<!-- CityGML Version No. 2.0, February 2012 -->
<!-- CityGML - GML 3.1.1 application schema for 3D city models -->
<!-- International encoding standard of the Open Geospatial Consortium, see http://www.opengeospatial.org/standards/citygml -->
<!-- Jointly developed by the Special Interest Group 3D (SIG 3D) of GDI-DE, see http://www.sig3d.org               -->
<!-- For further information see: http://www.citygml.org -->
<CityModel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/citygml/2.0"
	xmlns:xAL="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0" xmlns:xlink="http://www.w3.org/1999/xlink"
	xmlns:gml="http://www.opengis.net/gml" xmlns:dem="http://www.opengis.net/citygml/relief/2.0"
	xmlns:bldg="http://www.opengis.net/citygml/building/2.0"
	xsi:schemaLocation="http://www.opengis.net/citygml/building/2.0 ../../CityGML/building.xsd http://www.opengis.net/citygml/relief/2.0 ../../CityGML/relief.xsd">
	<gml:name>Simple 3D city model LOD4 without Appearance</gml:name>
	<gml:boundedBy>
		<gml:Envelope srsDimension="3" srsName="urn:ogc:def:crs,crs:EPSG::25832,crs:EPSG::5783">
			<gml:lowerCorner>458868.0 5438343.0 112.0</gml:lowerCorner>
			<gml:upperCorner>458892.0 5438362.0 117.0</gml:upperCorner>
		</gml:Envelope>
	</gml:boundedBy>
	<cityObjectMember>
		<bldg:Building gml:id="GML_7b1a5a6f-ddad-4c3d-a507-3eb9ee0a8e68">
			<gml:name>Example Building LOD4 </gml:name>
			<bldg:function codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_function.xml">1000</bldg:function>
			<bldg:yearOfConstruction>1985</bldg:yearOfConstruction>
			<bldg:roofType codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_roofType.xml">1030</bldg:roofType>
			<bldg:measuredHeight uom="#m">5.0</bldg:measuredHeight>
			<bldg:storeysAboveGround>1</bldg:storeysAboveGround>
			<bldg:storeyHeightsAboveGround uom="#m">3.0</bldg:storeyHeightsAboveGround>
			<bldg:boundedBy>
				<bldg:GroundSurface>
					<gml:name>Ground Slab</gml:name>
					<bldg:lod4MultiSurface>
						<gml:MultiSurface>
							<gml:surfaceMember>
								<gml:Polygon gml:id="GML_d3981803-d4b0-4b5b-969c-53f657594757">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458875 5438355 112 458885 5438355 112 458885 5438350 112 458875 5438350 112 458875 5438355 112
											</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod4MultiSurface>
				</bldg:GroundSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface>
					<gml:name>Wall South</gml:name>
					<bldg:lod4MultiSurface>
						<gml:MultiSurface>
							<gml:surfaceMember>
								<gml:CompositeSurface gml:id="GML_1d350a50-6acc-4d3c-8c28-326ca4305fd1">
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10204_1916_571790_369478">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458878.5 5438350 113.2 458878.5 5438350 114.2 458878.5 5438350.1 114.2 458878.5 5438350.1
														113.2 458878.5 5438350 113.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10205_105_876837_53833">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458875 5438350 112 458885 5438350 112 458885 5438350 115 458875 5438350 115 458875 5438350
														112 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
											<gml:interior>
												<gml:LinearRing>
													<gml:posList>458877 5438350 114.2 458878.5 5438350 114.2 458878.5 5438350 113.2 458877 5438350 113.2
														458877 5438350 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:interior>
											<gml:interior>
												<gml:LinearRing>
													<gml:posList>458881.5 5438350 114.2 458883 5438350 114.2 458883 5438350 113.2 458881.5 5438350 113.2
														458881.5 5438350 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:interior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10206_1133_78310_431691">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458881.5 5438350 114.2 458881.5 5438350 113.2 458881.5 5438350.1 113.2 458881.5 5438350.1
														114.2 458881.5 5438350 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10207_170_321284_424514">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458883 5438350 114.2 458881.5 5438350 114.2 458881.5 5438350.1 114.2 458883 5438350.1 114.2
														458883 5438350 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10208_1773_608580_43387">
											<gml:exterior>
												<gml:LinearRing gml:id="PolyID10208_1773_608580_43387_0">
													<gml:posList>458878.5 5438350 114.2 458877 5438350 114.2 458877 5438350.1 114.2 458878.5 5438350.14
														114.2 458878.5 5438350 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10209_1571_771435_238540">
											<gml:exterior>
												<gml:LinearRing gml:id="PolyID10209_1571_771435_238540_0">
													<gml:posList>458881.5 5438350 113.2 458883 5438350 113.2 458883 5438350.1 113.2 458881.5 5438350.1 113.2
														458881.5 5438350 113.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10210_599_287520_415766">
											<gml:exterior>
												<gml:LinearRing gml:id="PolyID10210_599_287520_415766_0">
													<gml:posList>458883 5438350 113.2 458883 5438350 114.2 458883 5438350.1 114.2 458883 5438350.1 113.2
														458883 5438350 113.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10211_1784_120327_382264">
											<gml:exterior>
												<gml:LinearRing gml:id="PolyID10211_1784_120327_382264_0">
													<gml:posList>458877 5438350 113.2 458878.5 5438350 113.2 458878.5 5438350.1 113.2 458877 5438350.1 113.2
														458877 5438350 113.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID10212_1143_394036_161326">
											<gml:exterior>
												<gml:LinearRing gml:id="PolyID10212_1143_394036_161326_0">
													<gml:posList>458877 5438350 114.2 458877 5438350 113.2 458877 5438350.1 113.2 458877 5438350.1 114.2
														458877 5438350 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod4MultiSurface>
					<bldg:opening>
						<bldg:Window gml:id="GML_3b09d6a5-4c24-4847-a8a2-e97475e3de47">
							<gml:name>Window South 1</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:Polygon gml:id="GML_5e07e2cc-c28c-480e-880f-dfdfe287bb9e">
											<gml:exterior>
												<gml:LinearRing gml:id="PolyID10213_1986_38589_374102_0">
													<gml:posList>458878.5 5438350.1 114.2 458877 5438350.1 114.2 458877 5438350.1 113.2 458878.5 5438350.1
														113.2 458878.5 5438350.1 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
						</bldg:Window>
					</bldg:opening>
					<bldg:opening>
						<bldg:Window gml:id="GML_f75f01cc-c584-4a62-b34a-4a0e2640550d">
							<gml:name>Window South 2</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:Polygon gml:id="GML_d0ea2b6b-7992-4284-9a20-957a6c5c1cea">
											<gml:exterior>
												<gml:LinearRing gml:id="PolyID10214_1496_142050_398240_0">
													<gml:posList>458883 5438350.1 114.2 458881.5 5438350.1 114.2 458881.5 5438350.1 113.2 458883 5438350.1
														113.2 458883 5438350.1 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
						</bldg:Window>
					</bldg:opening>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface>
					<gml:name>Wall North</gml:name>
					<bldg:lod4MultiSurface>
						<gml:MultiSurface>
							<gml:surfaceMember>
								<gml:Polygon gml:id="GML_d3909000-2f18-4472-8886-1c127ea67df1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList srsDimension="3">458885 5438355 112 458875 5438355 112 458875 5438355 115 458885 5438355 115
												458885 5438355 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod4MultiSurface>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface>
					<gml:name>Wall East</gml:name>
					<bldg:lod4MultiSurface>
						<gml:MultiSurface>
							<gml:surfaceMember>
								<gml:CompositeSurface gml:id="GML_6286ffa9-3811-4796-a92f-3fd037c8e668">
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID48550_1052_759732_38514">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458885 5438353 112.2 458885 5438353 114.2 458884.9 5438353 114.2 458884.9 5438353 112.2
														458885 5438353 112.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID48551_1224_68120_309441">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458885 5438353 114.2 458885 5438352 114.2 458884.9 5438352 114.2 458884.9 5438353 114.2
														458885 5438353 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID48552_1047_537781_300186">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458885 5438350 112 458885 5438355 112 458885 5438355 115 458885 5438352.5 117 458885
														5438350 115 458885 5438350 112 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
											<gml:interior>
												<gml:LinearRing>
													<gml:posList>458885 5438352 112.2 458885 5438353 112.2 458885 5438353 114.2 458885 5438352 114.2 458885
														5438352 112.2 </gml:posList>
												</gml:LinearRing>
											</gml:interior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID48553_202_602233_363079">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458885 5438352 114.2 458885 5438352 112.2 458884.9 5438352 112.2 458884.9 5438352 114.2
														458885 5438352 114.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="PolyID48553_202_602233_363800">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458885 5438352 112.2 458885 5438353 112.2 458884.9 5438353 112.2 458884.9 5438352 112.2
														458885 5438352 112.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod4MultiSurface>
					<bldg:opening>
						<bldg:Door gml:id="GML_93096bbb-5155-47fb-ae2c-e2f9327f3007">
							<gml:name>Door East</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:Polygon gml:id="GML_8f988da9-22d7-41e5-ae94-880afd46a3c9">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458884.9 5438352 112.2 458884.9 5438353 112.2 458884.9 5438353 114.2 458884.9 5438352 114.2
														458884.9 5438352 112.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
						</bldg:Door>
					</bldg:opening>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface>
					<gml:name>Wall West</gml:name>
					<bldg:lod4MultiSurface>
						<gml:MultiSurface>
							<gml:surfaceMember>
								<gml:Polygon gml:id="GML_5cc4fd92-d5de-4dd8-971e-892c91da2d9f">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList srsDimension="3">458875 5438355 112 458875 5438350 112 458875 5438350 115 458875 5438352.5 117
												458875 5438355 115 458875 5438355 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod4MultiSurface>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface>
					<gml:name>Roof North</gml:name>
					<bldg:lod4MultiSurface>
						<gml:MultiSurface>
							<!-- Roof slab -->
							<gml:surfaceMember>
								<gml:Polygon gml:id="GML_ec6a8966-58d9-4894-8edd-9aceb91b923f">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList srsDimension="3">458885 5438355 115 458875 5438355 115 458875 5438352.5 117 458885 5438352.5
												117 458885 5438355 115 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<!-- Roof overhanging -->
							<gml:surfaceMember>
								<gml:Polygon gml:id="GML_70fa738e-80a4-4774-8a3b-322f037fa482">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458874.6 5438352.5 117 458875 5438352.5 117 458875 5438355 115 458885 5438355 115 458885
												5438352.5 117 458885.4 5438352.5 117 458885.4 5438355.312347524 114.75012198097823 458874.6
												5438355.312347524 114.75012198097823 458874.6 5438352.5 117 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod4MultiSurface>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface>
					<gml:name>Roof South</gml:name>
					<bldg:lod4MultiSurface>
						<!-- Roof slab -->
						<gml:MultiSurface>
							<gml:surfaceMember>
								<gml:Polygon gml:id="GML_b41dc792-5da6-4cd9-8f85-247583f305e3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList srsDimension="3">458875 5438350 115 458885 5438350 115 458885 5438352.5 117 458875 5438352.5
												117 458875 5438350 115 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<!-- Roof overhanging -->
							<gml:surfaceMember>
								<gml:Polygon gml:id="GML_db6d8edc-4870-4523-a606-d440f36f8ec8">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458885.4 5438349.687652476 114.75012198097823 458885.4 5438352.5 117 458885 5438352.5 117
												458885 5438350 115 458875 5438350 115 458875 5438352.5 117 458874.6 5438352.5 117 458874.6
												5438349.687652476 114.75012198097823 458885.4 5438349.687652476 114.75012198097823 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod4MultiSurface>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:lod4Solid>
				<gml:Solid>
					<gml:exterior>
						<gml:CompositeSurface>
							<!-- Ground Slab -->
							<gml:surfaceMember xlink:href="#GML_d3981803-d4b0-4b5b-969c-53f657594757"/>
							<!-- Wall South -->
							<gml:surfaceMember xlink:href="#GML_1d350a50-6acc-4d3c-8c28-326ca4305fd1"/>
							<!-- Window South 1 -->
							<gml:surfaceMember xlink:href="#GML_5e07e2cc-c28c-480e-880f-dfdfe287bb9e"/>
							<!-- Window South 2 -->
							<gml:surfaceMember xlink:href="#GML_d0ea2b6b-7992-4284-9a20-957a6c5c1cea"/>
							<!-- Wall North -->
							<gml:surfaceMember xlink:href="#GML_d3909000-2f18-4472-8886-1c127ea67df1"/>
							<!-- Wall East -->
							<gml:surfaceMember xlink:href="#GML_6286ffa9-3811-4796-a92f-3fd037c8e668"/>
							<!-- Door East -->
							<gml:surfaceMember xlink:href="#GML_8f988da9-22d7-41e5-ae94-880afd46a3c9"/>
							<!-- Wall West -->
							<gml:surfaceMember xlink:href="#GML_5cc4fd92-d5de-4dd8-971e-892c91da2d9f"/>
							<!-- Roof North -->
							<gml:surfaceMember xlink:href="#GML_ec6a8966-58d9-4894-8edd-9aceb91b923f"/>
							<!-- Roof South -->
							<gml:surfaceMember xlink:href="#GML_b41dc792-5da6-4cd9-8f85-247583f305e3"/>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod4Solid>
			<bldg:interiorRoom>
				<bldg:Room>
					<bldg:lod4Solid>
						<gml:Solid>
							<gml:exterior>
								<gml:CompositeSurface>
									<!-- Floor -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="-">
											<gml:baseSurface xlink:href="#GML_fa89e511-39b2-46de-9a13-9f4621576a46"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Interior Wall North -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="-">
											<gml:baseSurface xlink:href="#GML_592ce9fa-0b98-4225-8d22-20eff4f86fc5"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Interior Wall West -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="-">
											<gml:baseSurface xlink:href="#GML_a9fe597d-c338-43ad-a633-2a0beb273fac"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Interior Wall East -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="-">
											<gml:baseSurface xlink:href="#GML_eaf1db16-56a3-4b86-ae19-2edbb604636f"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Door East -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="+">
											<gml:baseSurface xlink:href="#GML_8f988da9-22d7-41e5-ae94-880afd46a3c9"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Interior Wall South -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="-">
											<gml:baseSurface xlink:href="#GML_a718c157-c948-42cf-a786-0ce61044cff9"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Window South 1 -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="+">
											<gml:baseSurface xlink:href="#GML_5e07e2cc-c28c-480e-880f-dfdfe287bb9e"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Window South 2 -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="+">
											<gml:baseSurface xlink:href="#GML_d0ea2b6b-7992-4284-9a20-957a6c5c1cea"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Ceiling North -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="-">
											<gml:baseSurface xlink:href="#GML_989aa5cf-ee07-4fd8-89b6-500a9d5ba8041"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
									<!-- Ceiling South -->
									<gml:surfaceMember>
										<gml:OrientableSurface orientation="-">
											<gml:baseSurface xlink:href="#GML_98841838-ee0b-402f-ba28-64ed61cb10f8"/>
										</gml:OrientableSurface>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</bldg:lod4Solid>
					<bldg:boundedBy>
						<bldg:InteriorWallSurface>
							<gml:name>Interior Wall North</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:Polygon gml:id="GML_592ce9fa-0b98-4225-8d22-20eff4f86fc5">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458875.2 5438354.8 112.2 458884.8 5438354.8 112.2 458884.8 5438354.8 114.90387503050269
														458875.2 5438354.8 114.90387503050269 458875.2 5438354.8 112.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
						</bldg:InteriorWallSurface>
					</bldg:boundedBy>
					<bldg:boundedBy>
						<bldg:InteriorWallSurface>
							<gml:name>Interior Wall West</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:Polygon gml:id="GML_a9fe597d-c338-43ad-a633-2a0beb273fac">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458875.2 5438350.2 112.2 458875.2 5438354.8 112.2 458875.2 5438354.8 114.90387503050269
														458875.2 5438352.5 116.74387503050269 458875.2 5438350.2 114.90387503050269 458875.2 5438350.2 112.2
													</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
						</bldg:InteriorWallSurface>
					</bldg:boundedBy>
					<bldg:boundedBy>
						<bldg:InteriorWallSurface>
							<gml:name>Interior Wall East</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:CompositeSurface gml:id="GML_eaf1db16-56a3-4b86-ae19-2edbb604636f">
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_ec38f21c-daee-4610-aa55-87b6ac956d3a">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458884.8 5438352 112.2 458884.8 5438352 114.2 458884.9 5438352 114.2 458884.9 5438352
																114 458884.9 5438352 112.2 458884.8 5438352 112.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_7d51f0d1-f3ed-4683-a25c-577bb0f1a537">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458884.8 5438352 114.2 458884.8 5438353 114.2 458884.9 5438353 114.2 458884.9 5438352
																114.2 458884.8 5438352 114.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_0aa5c970-e574-4ced-9048-80a84b3b6661">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458884.8 5438353 114.2 458884.8 5438353 112.2 458884.9 5438353 112.2 458884.9 5438353
																114 458884.9 5438353 114.2 458884.8 5438353 114.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_d86e14ef-90d0-4331-b9ba-42fc869639c2">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458884.8 5438354.8 112.2 458884.8 5438353 112.2 458884.8 5438353 114.2 458884.8 5438352
																114.2 458884.8 5438352 112.2 458884.8 5438350.2 112.2 458884.8 5438350.2 114.90387503050269
																458884.8 5438352.5 116.74387503050269 458884.8 5438354.8 114.90387503050269 458884.8 5438354.8
																112.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
										</gml:CompositeSurface>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
							<bldg:opening>
								<bldg:Door>
									<gml:name>Door East</gml:name>
									<bldg:lod4MultiSurface>
										<gml:MultiSurface>
											<gml:surfaceMember>
												<gml:OrientableSurface orientation="-">
													<gml:baseSurface xlink:href="#GML_8f988da9-22d7-41e5-ae94-880afd46a3c9"> </gml:baseSurface>
												</gml:OrientableSurface>
											</gml:surfaceMember>
										</gml:MultiSurface>
									</bldg:lod4MultiSurface>
								</bldg:Door>
							</bldg:opening>
						</bldg:InteriorWallSurface>
					</bldg:boundedBy>
					<bldg:boundedBy>
						<bldg:InteriorWallSurface>
							<gml:name>Interior Wall South</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:CompositeSurface gml:id="GML_a718c157-c948-42cf-a786-0ce61044cff9">
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_473580a9-fc2c-4a04-a551-e24a256688a8">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458878.5 5438350.2 114.2 458878.5 5438350.2 113.2 458878.5 5438350.1 113.2 458878.5
																5438350.1 114 458878.5 5438350.1 114.2 458878.5 5438350.2 114.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_f9f9ee66-75f9-4119-a574-550be589e88c">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458883 5438350.2 114.2 458883 5438350.2 113.2 458883 5438350.1 113.2 458883 5438350.1
																114 458883 5438350.1 114.2 458883 5438350.2 114.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_e3415d97-1d1f-4edc-aa3d-f58185c1c99d">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458878.5 5438350.2 113.2 458877 5438350.2 113.2 458877 5438350.1 113.2 458878.5
																5438350.1 113.2 458878.5 5438350.2 113.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_0c892a7e-1c5b-4c12-8b92-949daede3313">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458877 5438350.2 114.2 458878.5 5438350.2 114.2 458878.5 5438350.1 114.2 458877
																5438350.1 114.2 458877 5438350.2 114.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_a7dc026d-ab34-486c-a406-f4ed3221c729">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458877 5438350.2 113.2 458877 5438350.2 114.2 458877 5438350.1 114.2 458877 5438350.1
																114 458877 5438350.1 113.2 458877 5438350.2 113.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_bb68f3bc-748d-44c5-a57b-6d346e880c3c">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458883 5438350.2 113.2 458881.5 5438350.2 113.2 458881.5 5438350.1 113.2 458883
																5438350.1 113.2 458883 5438350.2 113.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_cf0b79ba-f31f-4bae-a10f-5bcc85ce2cf6">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458884.8 5438350.2 112.2 458875.2 5438350.2 112.2 458875.2 5438350.2 114.90387503050269
																458884.8 5438350.2 114.90387503050269 458884.8 5438350.2 112.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
													<gml:interior>
														<gml:LinearRing>
															<gml:posList>458877 5438350.2 113.2 458878.5 5438350.2 113.2 458878.5 5438350.2 114.2 458877
																5438350.2 114.2 458877 5438350.2 113.2 </gml:posList>
														</gml:LinearRing>
													</gml:interior>
													<gml:interior>
														<gml:LinearRing>
															<gml:posList>458883 5438350.2 113.2 458883 5438350.2 114.2 458881.5 5438350.2 114.2 458881.5
																5438350.2 113.2 458883 5438350.2 113.2 </gml:posList>
														</gml:LinearRing>
													</gml:interior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_d717483a-d2b2-4862-92ee-4bea7216f2ab">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458881.5 5438350.2 114.2 458883 5438350.2 114.2 458883 5438350.1 114.2 458881.5
																5438350.1 114.2 458881.5 5438350.2 114.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
											<gml:surfaceMember>
												<gml:Polygon gml:id="GML_73ab206b-c69a-4d13-b498-df812c7a2091">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>458881.5 5438350.2 113.2 458881.5 5438350.2 114.2 458881.5 5438350.1 114.2 458881.5
																5438350.1 114 458881.5 5438350.1 113.2 458881.5 5438350.2 113.2 </gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
										</gml:CompositeSurface>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
							<bldg:opening>
								<bldg:Window>
									<gml:name>Window South 1</gml:name>
									<bldg:lod4MultiSurface>
										<gml:MultiSurface>
											<gml:surfaceMember>
												<gml:OrientableSurface orientation="-">
													<gml:baseSurface xlink:href="#GML_5e07e2cc-c28c-480e-880f-dfdfe287bb9e"> </gml:baseSurface>
												</gml:OrientableSurface>
											</gml:surfaceMember>
										</gml:MultiSurface>
									</bldg:lod4MultiSurface>
								</bldg:Window>
							</bldg:opening>
							<bldg:opening>
								<bldg:Window>
									<gml:name>Window South 2</gml:name>
									<bldg:lod4MultiSurface>
										<gml:MultiSurface>
											<gml:surfaceMember>
												<gml:OrientableSurface orientation="-">
													<gml:baseSurface xlink:href="#GML_d0ea2b6b-7992-4284-9a20-957a6c5c1cea"> </gml:baseSurface>
												</gml:OrientableSurface>
											</gml:surfaceMember>
										</gml:MultiSurface>
									</bldg:lod4MultiSurface>
								</bldg:Window>
							</bldg:opening>
						</bldg:InteriorWallSurface>
					</bldg:boundedBy>
					<bldg:boundedBy>
						<bldg:FloorSurface>
							<gml:name>Floor</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:Polygon gml:id="GML_fa89e511-39b2-46de-9a13-9f4621576a46">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458884.8 5438354.8 112.2 458875.2 5438354.8 112.2 458875.2 5438350.2 112.2 458884.8
														5438350.2 112.2 458884.8 5438352 112.2 458884.9 5438352 112.2 458884.9 5438353 112.2 458884.8 5438353
														112.2 458884.8 5438354.8 112.2 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
						</bldg:FloorSurface>
					</bldg:boundedBy>
					<bldg:boundedBy>
						<bldg:CeilingSurface>
							<gml:name>Ceiling South</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:Polygon gml:id="GML_989aa5cf-ee07-4fd8-89b6-500a9d5ba8041">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458884.8 5438352.5 116.74387503050269 458884.8 5438350.2 114.90387503050269 458875.2
														5438350.2 114.90387503050269 458875.2 5438352.5 116.74387503050269 458884.8 5438352.5
														116.74387503050269 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
						</bldg:CeilingSurface>
					</bldg:boundedBy>
					<bldg:boundedBy>
						<bldg:CeilingSurface>
							<gml:name>Ceiling North</gml:name>
							<bldg:lod4MultiSurface>
								<gml:MultiSurface>
									<gml:surfaceMember>
										<gml:Polygon gml:id="GML_98841838-ee0b-402f-ba28-64ed61cb10f8">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>458875.2 5438352.5 116.74387503050269 458875.2 5438354.8 114.90387503050269 458884.8
														5438354.8 114.90387503050269 458884.8 5438352.5 116.74387503050269 458875.2 5438352.5
														116.74387503050269 </gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod4MultiSurface>
						</bldg:CeilingSurface>
					</bldg:boundedBy>
				</bldg:Room>
			</bldg:interiorRoom>
			<bldg:address>
				<Address>
					<xalAddress>
						<xAL:AddressDetails>
							<xAL:Country>
								<xAL:CountryName>Germany</xAL:CountryName>
								<xAL:Locality Type="Town">
									<xAL:LocalityName>Eggenstein-Leopoldshafen</xAL:LocalityName>
									<xAL:Thoroughfare Type="Street">
										<xAL:ThoroughfareNumber>1</xAL:ThoroughfareNumber>
										<xAL:ThoroughfareName>Hermann-von-Helmholtz-Platz</xAL:ThoroughfareName>
									</xAL:Thoroughfare>
									<xAL:PostalCode>
										<xAL:PostalCodeNumber>76344</xAL:PostalCodeNumber>
									</xAL:PostalCode>
								</xAL:Locality>
							</xAL:Country>
						</xAL:AddressDetails>
					</xalAddress>
					<multiPoint>
						<gml:MultiPoint>
							<gml:pointMember>
								<gml:Point>
									<gml:pos srsDimension="3">458880.0 5438352.6 112.0 </gml:pos>
								</gml:Point>
							</gml:pointMember>
						</gml:MultiPoint>
					</multiPoint>
				</Address>
			</bldg:address>
		</bldg:Building>
	</cityObjectMember>
	<cityObjectMember>
		<dem:ReliefFeature gml:id="GML_6bb30328-7599-4500-90ef-766fde6aa67b">
			<gml:name>Example TIN LOD4</gml:name>
			<dem:lod>3</dem:lod>
			<dem:reliefComponent>
				<dem:TINRelief gml:id="GUID_04D4DsNGv1MfvYu5O3lkcW">
					<gml:name>Ground</gml:name>
					<dem:lod>3</dem:lod>
					<dem:tin>
						<gml:TriangulatedSurface gml:id="ground">
							<gml:trianglePatches>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458868 5438362 112 458875 5438355 112 458883 5438362 114 458868 5438362 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458875 5438355 112 458885 5438355 112 458883 5438362 114 458875 5438355 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458883 5438362 114 458885 5438355 112 458892 5438362 112 458883 5438362 114 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458885 5438355 112 458885 5438350 112 458892 5438362 112 458885 5438355 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458885 5438350 112 458892 5438343 112 458892 5438362 112 458885 5438350 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458875 5438350 112 458892 5438343 112 458885 5438350 112 458875 5438350 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458868 5438343 112 458892 5438343 112 458875 5438350 112 458868 5438343 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458868 5438343 112 458875 5438350 112 458875 5438355 112 458868 5438343 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
								<gml:Triangle>
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>458868 5438343 112 458875 5438355 112 458868 5438362 112 458868 5438343 112 </gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Triangle>
							</gml:trianglePatches>
						</gml:TriangulatedSurface>
					</dem:tin>
				</dem:TINRelief>
			</dem:reliefComponent>
		</dem:ReliefFeature>
	</cityObjectMember>
</CityModel>
