import numpy as np
import pandas as pd

import geoplot as gplt
import geopandas as gpd
import geoplot.crs as gcrs
import imageio
import pathlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import mapclassify as mc
import fiona
from matplotlib import colors
norm = colors.Normalize(vmin=-1, vmax=1)

import math

#### load crash data #####################################################################################
##### can be found at ####################################################################################
##### https://opendata-nzta.opendata.arcgis.com/datasets/NZTA::crash-analysis-system-cas-data-1/about ####
file = pd.read_csv("Crash_Analysis_System_(CAS)_data.csv")

#### load in Stats annual pop. est. data #################################################################
##### can be found in project folder #####################################################################
popFile = pd.read_csv("pop-esti-StatsNZ-2000-2021.csv")

#### load in census work-travel data #####################################################################
##### can be found in project folder #####################################################################
census_WT_2018 = pd.read_csv("census-work-travel-2018.csv")
census_WT_2001_13 = pd.read_csv("census-work-travel-2001-2006-2013.csv")

###### load map data #####################################################################################
###### can be found at (sign-up requiered for download)  #################################################
###### https://datafinder.stats.govt.nz/layer/106667-regional-council-2022-clipped-generalised/ ##########
gdb_file = "regional-council-2022-clipped-generalised.gdb"
layers = fiona.listlayers(gdb_file)

for layer in layers:
        gdf = gpd.read_file(gdb_file,layer=layer)

#### reset column and row display #####
pd.set_option('display.max_columns',72)
pd.set_option('display.max_rows',79)

######view files ########
file.head(5)
file.tail(5)

popFile.head(5)

census_WT_2001_13.head(5)
census_WT_2018.head(5)

file.info()
file.isna().sum()

popFile.info()
popFile.isna().sum()

census_WT_2001_13.info()
census_WT_2001_13.isna().sum()

census_WT_2018.info()
census_WT_2018.isna().sum()

tes = pd.DataFrame(file.isna().sum(), columns=['null'])

tes.unstack().reset_index(name='nullc').groupby('nullc').count()



#### set missing region and tlaName to unknown ####
values = {"region": 'unknown', "tlaName" : 'unknown'}
fileFill = file.fillna(value=values)

########## finding meshblockes that have unknown regions #####
file[["meshblockId", "region"]].drop_duplicates().groupby('meshblockId').count().count()
file[["meshblockId", "region"]].drop_duplicates().groupby('meshblockId').count().query('region > 1').count()
lap = file[["meshblockId", "region"]].drop_duplicates().groupby('meshblockId').count().query('region > 1')


meshblock_region_counts = fileFill[["meshblockId", "region"]].value_counts().reset_index(name='meshblock_region_count')
repeated_meshblocks = fileFill[["meshblockId", "region"]].drop_duplicates().groupby('meshblockId').count().query('region > 1')
ping = pd.merge(meshblock_region_counts, repeated_meshblocks, how='inner', on='meshblockId')


############# finding non unique mashblock with additional unknown region ##### 
pd.merge(meshblock_region_counts, repeated_meshblocks, how='inner', on='meshblockId').groupby(["region_y"]).count()

pd.merge(meshblock_region_counts, repeated_meshblocks, how='inner', on='meshblockId').query('region_y > 2')


############# number of crashes per region with non unique mashblock ##### 
pd.merge(meshblock_region_counts, repeated_meshblocks, how='inner', on='meshblockId').groupby(["region_x"]).sum()[['meshblock_region_count']]

########### List of meshblock IDs with two regions ######
pd.merge(lap, ping, how='left', on='meshblockId')
###### for a few of these number of crashes in both region are quite simelar ###



meshblocks_with_unknown=pd.merge(meshblock_region_counts, repeated_meshblocks, how='inner', on='meshblockId').query('`region_x` == "unknown" ')
meshblocks_with_unknown

meshblocks_with_unknowns_filtered_out = pd.merge(meshblock_region_counts, repeated_meshblocks, how='inner', on='meshblockId').query('`region_x` != "unknown" ')
meshblocks_with_unknowns_filtered_out

tes1R=meshblocks_with_unknowns_filtered_out[meshblocks_with_unknowns_filtered_out.meshblockId.isin(meshblocks_with_unknown.meshblockId)]

tes1R
tes2R = tes1R[["meshblockId","region_x"]].drop_duplicates(subset=['meshblockId'], keep='first')
tes2R.query('meshblockId == 135100.')
tes2R


########### Crash data with imputation of regions using meshBlocks  ###############
dfR = pd.merge(file, tes2R, how='left', on='meshblockId')
dfR.loc[dfR['region'].isnull(),'region'] = dfR['region_x']

############ Most of the unknown crashes in these two meshBlocks are on the #########
############# AUCKLAND HARBOUR BRIDGE (SH 1 or SH 1N)  ######################### 
fileFill.query('`crashLocation2` == "TOP OF HARBOUR BRIDGE"').groupby(['region','meshblockId']).count()

fileFill.query( 'meshblockId == 423600').groupby(['region','crashLocation2']).count()
fileFill.query( 'meshblockId == 423600').groupby(['region','crashLocation1']).count()

fileFill.query( 'meshblockId == 359300').groupby(['region','crashLocation2']).count()
fileFill.query( 'meshblockId == 359300').groupby(['region','crashLocation1']).count()
############# with over a 1000 crashes this is a third of the missing entries ############ 

########### If all values are replaced with region there should be 116 missing entries left ####
dfR[['region']].isna().sum()
########### Sadly it is 135 hence up to 19 meshblocks have only crashes with unknown region #############

############### finding area units that have unknown regions #####
file[["areaUnitID"]].drop_duplicates().count()
file[["areaUnitID", "region"]].drop_duplicates().groupby('areaUnitID').count().count()
file[["areaUnitID", "region"]].drop_duplicates().groupby('areaUnitID').count().query('region > 1').count()
lapA = file[["areaUnitID", "region"]].drop_duplicates().groupby('areaUnitID').count().query('region > 1')


areaUnitID_region_counts = fileFill[["areaUnitID", "region"]].value_counts().reset_index(name='areaUnitID_region_count')
repeated_areaUnitID = fileFill[["areaUnitID", "region"]].drop_duplicates().groupby('areaUnitID').count().query('region > 1')
pingA = pd.merge(areaUnitID_region_counts, repeated_areaUnitID, how='inner', on='areaUnitID')
pd.merge(areaUnitID_region_counts, repeated_areaUnitID, how='inner', on='areaUnitID').groupby(["region_y"]).count()
pd.merge(areaUnitID_region_counts, repeated_areaUnitID, how='inner', on='areaUnitID').query('region_y > 2')

pd.merge(areaUnitID_region_counts, repeated_areaUnitID, how='inner', on='areaUnitID').query('region_y > 2').groupby(["region_x"]).sum()

pd.merge(areaUnitID_region_counts, repeated_areaUnitID, how='inner', on='areaUnitID').groupby(["region_x"]).sum()

pd.merge(lapA, pingA, how='left', on='areaUnitID')

areaUnitID_with_unknown=pd.merge(areaUnitID_region_counts, repeated_areaUnitID, how='inner', on='areaUnitID').query('`region_x` == "unknown" ')
areaUnitID_with_unknown

areaUnitID_with_unknowns_filtered_out = pd.merge(areaUnitID_region_counts, repeated_areaUnitID, how='inner', on='areaUnitID').query('`region_x` != "unknown" ')
areaUnitID_with_unknowns_filtered_out

tes1A=areaUnitID_with_unknowns_filtered_out[areaUnitID_with_unknowns_filtered_out.areaUnitID.isin(areaUnitID_with_unknown.areaUnitID)]

tes1A
tes2A = tes1A[["areaUnitID","region_x"]].drop_duplicates(subset=['areaUnitID'], keep='first')
tes2A.query('areaUnitID == 505010.|areaUnitID == 506660.|areaUnitID == 505021.|areaUnitID == 521153.|areaUnitID == 521151.')
tes2A

########### Crash data with imputation of regions using AreaUnits  ###############
dfA = pd.merge(file, tes2A, how='left', on='areaUnitID')
dfA.loc[dfA['region'].isnull(),'region'] = dfA['region_x']

dfA

########### If all values are replaced with region there should be 116 missing entries left ####

dfA[['region']].isna().sum()

########### Cross Checking if the imputation is likley to be the same as for the imputation mashblocks ####
########### First line should have no negative entries ####################################################
########### Second line should be 19 ######################################################################
dfA[['region','X']].groupby('region').count() - dfR[['region','X']].groupby('region').count()
(dfA[['region','X']].groupby('region').count() - dfR[['region','X']].groupby('region').count()).sum()


########## Started doing the same for tlaNames but did not finish ########### 
########## finding area unites that have unknown tlaName_counts #############
areaUnitID_tlaName_counts = fileFill[["areaUnitID", "tlaName"]].value_counts().reset_index(name='meshblock_tlaName_count')
repeated_areaUnitID_tlc = fileFill[["areaUnitID", "tlaName"]].drop_duplicates().groupby('areaUnitID').count().query('tlaName > 1')
pd.merge(areaUnitID_tlaName_counts, repeated_areaUnitID_tlc, how='inner', on='areaUnitID')
pd.merge(areaUnitID_tlaName_counts, repeated_areaUnitID_tlc, how='inner', on='areaUnitID').groupby(["tlaName_y"]).count()
pd.merge(areaUnitID_tlaName_counts, repeated_areaUnitID_tlc, how='inner', on='areaUnitID').query('tlaName_y > 2')


########## finding meshblockes that have unknown tlaName_counts #####
meshblock_tlaName_counts = fileFill[["meshblockId", "tlaName"]].value_counts().reset_index(name='meshblock_tlaName_count')
repeated_meshblocks_tlc = fileFill[["meshblockId", "tlaName"]].drop_duplicates().groupby('meshblockId').count().query('tlaName > 1')
pd.merge(meshblock_tlaName_counts, repeated_meshblocks_tlc, how='inner', on='meshblockId')
pd.merge(meshblock_tlaName_counts, repeated_meshblocks_tlc, how='inner', on='meshblockId').groupby(["tlaName_y"]).count()
pd.merge(meshblock_tlaName_counts, repeated_meshblocks_tlc, how='inner', on='meshblockId').query('tlaName_y > 2')
pd.merge(meshblock_tlaName_counts, repeated_meshblocks_tlc, how='inner', on='meshblockId').iloc[0:30]

fileFill[["meshblockId", "tlaName"]].value_counts()

##### renaming the population file colums ########
popfileB = popFile[['Area','Year at 30 June','Value']].rename(columns = {'Area':'region','Year at 30 June':'crashYear','Value':'population'})
popfileB

##### renaming census file colums ########
census_WT_2018_B = census_WT_2018[['Area', 'Main means of travel to work', 'Year', 'Value' ]].rename(columns = {'Area':'region','Main means of travel to work':'Travel to work'})
census_WT_2001_13_B = census_WT_2001_13[['Area', 'Main means of travel to work', 'Year', 'Value']].rename(columns = {'Area':'region','Main means of travel to work':'Travel to work'})

####### Joining the census files ######
census_WT= pd.concat([census_WT_2001_13_B ,census_WT_2018_B]).reset_index().drop(['index'], axis=1)
census_WT.groupby(["Travel to work"]).count()


####### To take the 'Total people - main means of travel to work' #####
######## as total for the ratio of (walker + cyclist)/worker ##########
######## makes the ratio of the 2018 cencus roughly compable ##########
######## to the preivous ones #########################################
###### adjusting columns names ########################################
census_WT['Travel to work'] = census_WT['Travel to work'].replace(['Drove a company car, truck or van','Drove a private car, truck or van','Walked or jogged','Worked at home','Total people, main means of travel to work'],['Drive a company car, truck or van','Drive a private car, truck or van','Walk or jog','Work at home', 'Total people - main means of travel to work'])

census_WT

census_WT.groupby(["Travel to work"]).count()

census_WT.query('`Travel to work` == "Total people stated" ')
census_WT.query('`Travel to work` == "Did not go to work today" ')
census_WT.query('`Travel to work` == "Total people, main means of travel to work" ')
census_WT.query('`Travel to work` == "Not elsewhere included" ')
census_WT.query('`Travel to work` == "Other" ')

census_WT.query('`region` == "Total New Zealand" ')


census_WT.pivot(index=('Year', 'region'), columns='Travel to work', values='Value').reset_index()

pd.set_option('display.max_rows',20)

census_WTmatX = census_WT.pivot(index=('Year', 'region'), columns='Travel to work', values='Value')



census_WTmat = census_WT.pivot(index=('Year', 'region'), columns='Travel to work', values='Value').reset_index()


########### Taking the columns Of interest and calculate (walker + cyclist)/worker ###
totWP=census_WTmat['Total people - main means of travel to work']
totBi =census_WTmat['Bicycle']
totWa =census_WTmat['Walk or jog']
 
RatBi =  totBi/totWP

Rate_Walk_Bike = (totBi+totWa)/totWP


region_Walk_Bike = census_WTmat[['Year','region']].assign( Walk_Bike = (totBi+totWa))


region_Walk_Bike_rate = census_WTmat[['Year','region']].assign(Rate_Walk_Bike = (totBi+totWa)/totWP)

region_Walk_Bike_rate.query('`region` == "Total New Zealand" ')
region_Walk_Bike_rate.query('`region` == "Wellington Region" ')
region_Walk_Bike_rate.query('`region` == "Auckland Region" ')



##### transforming crash count per year to same format as population data ####  
RegT = dfA[[ "region","crashYear",'X']].groupby([ "region","crashYear"]).count().unstack(level = [0,1] ).reset_index(name='crashCount')

RegT

RegTTotal = RegT.groupby(["crashYear"]).sum().assign(region = 'Total New Zealand').reset_index()

RegTTotal

RegTT = pd.concat([RegT,RegTTotal])

RegTT.tail(22)


cashCouT_PoP = pd.merge(RegTT, popfileB, how='left', on=('crashYear','region'))
cashCouT_PoP.tail(22)

cashCouT_PoP.head(16)

cashCountTotalPerPoP = cashCouT_PoP.assign(CrashPerPop = cashCouT_PoP['crashCount']/cashCouT_PoP['population'])

cashCountTotalPerPoPA = cashCountTotalPerPoP[['crashYear','region', 'CrashPerPop']].pivot(index=('crashYear'), columns='region')

cashCountTotalPerPoPA.columns = cashCountTotalPerPoPA.columns.droplevel()

cashCountTotalPerPoPA


##### transforming crash servity count per year to same format as population data ####  
RegZ = dfA[["crashSeverity" ,"region","crashYear",'X']].groupby(["crashSeverity", "region","crashYear"]).count().unstack(level = [-1,0,1] ).reset_index(name='crashCount')
RegZZZ = RegZ.pivot(index=('crashYear', 'region'), columns='crashSeverity', values='crashCount').reset_index()

RegZZZ

RegZZTotal = RegZZZ.groupby(["crashYear"]).sum().assign(region = 'Total New Zealand').reset_index()

#RegZZTotal
RegZZ = pd.concat([RegZZZ,RegZZTotal])

RegZZ.tail(22)


cashCou_PoP = pd.merge(RegZZ, popfileB, how='left', on=('crashYear','region'))
cashCou_PoP.tail(22)

cashCou_PoP.head(16)

cashCountPerPoP = cashCou_PoP.assign(fatalCrashPerPop = cashCou_PoP['Fatal Crash']/cashCou_PoP['population'], SeriousCrashPerPop = cashCou_PoP['Serious Crash']/cashCou_PoP['population'], MinorCrashPerPop = cashCou_PoP['Minor Crash']/cashCou_PoP['population'], NonInjuryCrashPerPop = cashCou_PoP['Non-Injury Crash']/cashCou_PoP['population'])

cashCountPerPoPA =cashCountPerPoP[['crashYear','region', 'fatalCrashPerPop', 'SeriousCrashPerPop' , 'MinorCrashPerPop', 'NonInjuryCrashPerPop']].pivot(index=('crashYear'), columns='region')


cashCountPerPoPA_Year =cashCountPerPoP[['crashYear','region', 'fatalCrashPerPop', 'SeriousCrashPerPop' , 'MinorCrashPerPop', 'NonInjuryCrashPerPop']].rename(columns={"crashYear": "Year"}).pivot(index=('Year'), columns='region')

cashCountPerPoPA

cashCountPerPoPA_Year

RegZZ.info()
popfileB.info()


#######################################################################################################
######### Exploring and ploting data ##################################################################
#######################################################################################################
file.groupby("crashSeverity").count()

file[["crashSeverity","crashYear","X"]].groupby(["crashSeverity","crashYear"]).count().head(22)
file[["fatalCount","crashYear"]].groupby(["crashYear"]).sum().head(22)

file.groupby("vanOrUtility").count()

file.groupby("tlaName").count().head(20)
#`region_x` == "unknown"

file.query('minorInjuryCount>0 & `crashSeverity` == "Non-Injury Crash" ')

file[["crashYear","crashSeverity","bridge"]].groupby(["crashYear"]).sum()
file[["crashYear","crashSeverity","bridge"]].groupby(["crashSeverity"]).sum()

fileFill[["region","bridge"]].groupby(["region"]).sum()

fileFill[["crashSeverity","X",'region']].groupby(["region","crashSeverity"]).count()



missingInC = file[file['fatalCount'].isnull()]
missingInC.query('crashYear != 2020')

missingInC.groupby("region").count()
missingInC.groupby(["crashSeverity","crashYear"]).count()
missingInC

missingMesh = file[file['meshblockId'].isnull()]
missingMesh.groupby(["crashSeverity","crashYear"]).count()
file


missingbridge = file[file['bridge'].isnull()]
missingbridge.groupby(["region","crashSeverity"]).count()
missingbridge[missingbridge["region"].isnull()].query('meshblockId == 423600')

file.query('meshblockId == 423600 & bridge >0')

file.groupby(["speedLimit", "crashSeverity"]).count()

file.groupby("speedLimit").count()

file.groupby("crashYear").count()

file.groupby("region").count()

file.groupby("region").sum()


RegY = file.groupby(["region","crashYear"]).count()
 
file.groupby(["urban", "crashSeverity"]).count()    
    
    
    
RegY.head(22)    

RegY.tail(22)

RegY.query('crashYear > 2018')





file.query('speedLimit == 2.0')
file.query('speedLimit == 5.0')
file.query('speedLimit == 6.0')


sim = file.query('areaUnitID == 525420.0')

sim.groupby('crashYear')

df  = file[file['areaUnitID'].isnull()]
df.head(10) 

df.query('crashYear != 2021')

dfn = file[file['region'].isnull()]


dfn.query('crashYear == 2021')
dfn.groupby("crashSeverity").count()

file.select_dtypes(exclude=['object'])

file.groupby("crashYear").count()

fileA = file[['region','crashYear' ,'fatalCount','seriousInjuryCount', 'minorInjuryCount','bus', 'bicycle', 'pedestrian','moped', 'motorcycle','carStationWagon','suv','schoolBus','taxi','truck','otherVehicleType','vehicle','vanOrUtility','otherObject']]

QW1 = fileA.groupby(["region","crashYear"]).sum()
QW1.head(22) 

QW1.tail(44)

fileA.groupby("crashYear").sum()

QW2 =file.groupby(["crashYear", "crashSeverity"]).count()

QW2.query('crashYear > 2017')

file.groupby(["areaUnitID","region"]).count()

file.groupby(["meshblockId"]).count()

file.groupby(["areaUnitID"]).count()

file.groupby(["meshblockId","region"]).count()

file.groupby(["meshblockId"])[['region']].nunique().query('region > 1')
file[["meshblockId", "region"]].drop_duplicates()


meshblock_region_counts = file[["meshblockId", "region"]].value_counts().reset_index(name='meshblock_region_count')
repeated_meshblocks = file[["meshblockId", "region"]].drop_duplicates().groupby('meshblockId').count().query('region > 1')
pd.merge(meshblock_region_counts, repeated_meshblocks, how='inner', on='meshblockId')


meshblock_region_counts = file[["areaUnitID", "region"]].value_counts().reset_index(name='meshblock_region_count')
repeated_meshblocks = file[["areaUnitID", "region"]].drop_duplicates().groupby('areaUnitID').count().query('region > 1')
pd.merge(meshblock_region_counts, repeated_meshblocks, how='inner', on='areaUnitID')






file[['X','region','crashSeverity' , 'crashYear']]

Group_reg_Severity_Year_Count = dfA[['X','region','crashSeverity' , 'crashYear']].groupby(["crashYear","region","crashSeverity"]).count().unstack().unstack().fillna(0)


Group_reg_Year_Count = dfA[['X','region' ,'crashYear']].groupby(["crashYear","region"]).count().unstack()

Group_reg_Year_Count.columns = Group_reg_Year_Count.columns.droplevel()

Group_reg_Year_Count

Group_reg_Severity_Year_Count.columns = Group_reg_Severity_Year_Count.columns.droplevel()

Group_reg_Severity_Year_Count.iloc[:, [0,1,2,3,4,5,6,7,8,9,10]].plot(linestyle='-', marker='o')

Group_reg_Severity_Year_Count

Group_reg_Severity_Year_Count.iloc[:, [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]].plot(linestyle='-', marker='o').legend(title='Crash Count',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))

Group_reg_Severity_Year_Count.reset_index().loc[0:20].plot(x = 'crashYear').legend(title='Crash Count',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))
     
    

def ColD(numC):
    lis=[]
    for i in range(int(numC/2+1)):
        lis.append( (0,1- i/(numC/2+1), 1- i/(numC/2+1)) )
    for i in range(int(numC/2+1)+1):
        lis.append( (i/(numC/2+1) ,0,  i/(numC/2+1)) )    
    return(lis)

ColA = ColD(14) 
ColB = ColD(15) 

ColA



Group_reg_Severity_Year_Count.loc[:,'Fatal Crash'].plot(linestyle='-', marker='o', color =ColA).legend(title='Fatal Crash Count Total',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))
Group_reg_Severity_Year_Count.loc[:,'Serious Crash'].plot(linestyle='-', marker='o', color =ColA).legend(title='Serious Crash Count Total',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))
Group_reg_Severity_Year_Count.loc[:,'Minor Crash'].plot(linestyle='-', marker='o', color =ColA).legend(title='Minor Crash Count Total',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))
Group_reg_Severity_Year_Count.loc[:,'Non-Injury Crash'].plot(linestyle='-', marker='o', color =ColA).legend(title='Non-Injury Crash Count Total',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))



Group_reg_Year_Count.plot(linestyle='-', marker='o', color =ColA).legend(title='Crash Count Total',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))


cashCountPerPoPA.loc[:,'fatalCrashPerPop'].plot(linestyle='-', marker='o', color =ColB).legend(title='Fatal Crash Count per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))
cashCountPerPoPA.loc[:,'SeriousCrashPerPop'].plot(linestyle='-', marker='o', color =ColB).legend(title='Serious Crash Count per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))
cashCountPerPoPA.loc[:,'MinorCrashPerPop'].plot(linestyle='-', marker='o', color =ColB).legend(title='Minor Crash Count per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))
cashCountPerPoPA.loc[:,'NonInjuryCrashPerPop'].plot(linestyle='-', marker='o', color =ColB).legend(title='Non-Injury Crash Count per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))

cashCountTotalPerPoPA.plot(linestyle='-', marker='o', color =ColA).legend(title='Count Total per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))


cashCountPerPoPA.loc[:,'NonInjuryCrashPerPop'].plot(linestyle='-', marker='o', color =ColA).legend(title='Non-Injury Crash Count per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))

cashCountPerPoPA.loc[:,'NonInjuryCrashPerPop'].loc[:,['Auckland Region','Wellington Region']].plot(linestyle='-', marker='o', color =ColA).legend(title='Non-Injury Crash Count per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))
cashCountPerPoPA
region_Walk_Bike_rate.pivot(index=('Year'), columns='region', values='Rate_Walk_Bike')

Group_reg_Severity_Year_Count.loc[:,'Non-Injury Crash'].loc[:,['Auckland Region','Wellington Region']].plot(linestyle='-', marker='o', color =ColA).legend(title='Non-Injury Crash Count Total',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))

region_Walk_Bike_rate

###########Corelator for Total data #######
totalwb = region_Walk_Bike.pivot(index=('Year'), columns='region', values='Walk_Bike').iloc[:, [1, 2,3,4, 5,6,7,8,10,11,14,15,16,18,20,21,22]]    
       
df = dfA[['X','crashYear']].groupby(['crashYear']).count().rename(columns={"X": "Total New Zealand"})

    
mxT = totalwb.mean()
sxT = totalwb.std()

Group_reg_Year_Count_cenYR = Group_reg_Year_Count.query("crashYear==2001 | crashYear==2006 | crashYear==2013 | crashYear==2018") 

Group_reg_Year_Count_cenY =pd.merge(Group_reg_Year_Count_cenYR, df, how='inner', on='crashYear')



my_TcenY = Group_reg_Year_Count_cenY.mean()
sy_TcenY = Group_reg_Year_Count_cenY.std()

mulT = totalwb * Group_reg_Year_Count_cenY

sumMulT = mulT.sum()
sumMulT
corLT = (sumMulT - 4*mxT *my_TcenY)/(4* sxT * sy_TcenY)
corLT


###########Corelator for per population data #######
rate = region_Walk_Bike_rate.pivot(index=('Year'), columns='region', values='Rate_Walk_Bike').iloc[:, [1, 2,3,4, 5,6,7,8,10,11,14,15,16,18,20,21,22]]

mx = rate.mean()
sx = rate.std()

cashCountTotalPerPoPA_cenY = cashCountTotalPerPoPA.query("crashYear==2001 | crashYear==2006 | crashYear==2013 | crashYear==2018") 

my_cenY = cashCountTotalPerPoPA_cenY.mean()
sy_cenY = cashCountTotalPerPoPA_cenY.std()

mul = rate * cashCountTotalPerPoPA_cenY

sumMul = mul.sum()
sumMul
corL = (sumMul - 4*mx *my_cenY)/(4* sx * sy_cenY)



corLR =corL.rename_axis('Region')



CorLdf = pd.DataFrame(corLR)




ACorLdf = pd.concat([CorLdf.iloc[::-1].drop('Total New Zealand'),CorLdf.loc[['Total New Zealand']]])

CorLdfA= CorLdf.unstack().reset_index(name = 'Sample correlation coefficient')[['Region', 'Sample correlation coefficient']]

ACorLdf.plot.barh(legend=None,xlim=[-1, 1],).set_xlabel('Correlation coefficient')

plot = ACorLdf.plot.barh(legend=None,xlim=[-1, 1]).set_xlabel('Correlation coefficient')
plot.get_figure().savefig('correl.pdf', format='pdf', bbox_inches = "tight")

count_map = pd.merge(gdf, CorLdfA, left_on="REGC2022_V1_00_NAME", right_on="Region")

gplt.choropleth(count_map, hue='Sample correlation coefficient', cmap = 'bwr', legend=True, norm= norm)

norm = colors.Normalize(vmin=-1, vmax=1)
mapCoeplot = gplt.choropleth(count_map, hue='Sample correlation coefficient', cmap = 'bwr', legend=True, norm= norm)
mapCoeplot.get_figure().savefig('map_correl.png', format='png', bbox_inches = "tight", dpi=300)


rate.plot(linestyle='-', marker='o', color =ColB).legend(title='rate',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))


cashCountPerPoPA.loc[:,'NonInjuryCrashPerPop'].loc[:,['Auckland Region','Wellington Region', 'Total New Zealand']].plot(linestyle='-', marker='o', color =ColA).legend(title='Non-Injury Crash Count per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))


cashCountTotalPerPoPA.loc[:,['Auckland Region','Wellington Region', 'Total New Zealand']].plot(linestyle='-', marker='o').legend(title='Count Total per Population',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))



rate.loc[:,['Total New Zealand','Bay of Plenty Region','Canterbury Region','Gisborne Region',"Hawke's Bay Region",'Manawatū-Whanganui Region','Northland Region','Southland Region','Taranaki Region','Tasman Region','Waikato Region' ]].plot(linestyle='-', marker='o').legend(title='rate',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))

rate.loc[:,['Nelson Region','Otago Region','West Coast Region']].plot(linestyle='-', marker='o').legend(title='rate',title_fontsize=10,loc='center left', bbox_to_anchor=(1, 0.5))

rate






cashCountPerPoPA.loc[:,'NonInjuryCrashPerPop'].loc[:,['Total New Zealand','Auckland Region', 'Canterbury Region','Bay of Plenty Region','Wellington Region']].plot(linestyle='-', marker='o', legend= None).set_ylabel('Crashes per population')


ploR =cashCountPerPoPA.loc[:,'NonInjuryCrashPerPop'].loc[:,['Total New Zealand','Auckland Region', 'Canterbury Region','Bay of Plenty Region','Wellington Region']]

ploR.plot(linestyle='-', marker='o', legend= None,xlim=[2000, 2021]).set_xticks([2000,2005,2010,2015,2020])

cashCountPerPoPA.rename(index={"crashYear": "Year"})


fig2 = cashCountPerPoPA_Year.loc[:,'NonInjuryCrashPerPop'].loc[:,['Total New Zealand','Auckland Region', 'Canterbury Region','Bay of Plenty Region','Wellington Region']].plot(linestyle='-', marker='o', legend= None,xlim=[2000, 2021],ylim=[0, 0.01], xticks=(2000,2005,2010,2015,2020)).set_ylabel('Crashes per population')

fig1 = rate.loc[:,['Total New Zealand','Auckland Region', 'Canterbury Region','Bay of Plenty Region','Wellington Region']].plot(linestyle='-', marker='o',xlim=[2001, 2018],ylim=[0, 0.13]).set_ylabel('(walkers+cyclists)/workers')



fig1.get_figure().savefig('crash-talk/mod-work.pdf', format='pdf', bbox_inches = "tight")


fig2.get_figure().savefig('crash-talk/crash-per-pop.pdf', format='pdf', bbox_inches = "tight")
