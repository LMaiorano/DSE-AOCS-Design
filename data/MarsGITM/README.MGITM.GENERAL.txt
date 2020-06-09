***************************************************************************************

Date: 17-September-2019
Who: S. W. Bougher
General Details of MGITM datasets for PEDE Dust Event in Summer 2018

*****************************************************************************************

PEDE Dust Storm Campaigns (see Elrod et al., 2019; Jain et al., 2019)
--------------------------------------------------------------------------------------------
Interval   Date (2018)    Season (Ls)  Periapsis Latitude  Periapsis TLST    Narrative
                                            (DEG)             (Hours)
--------------------------------------------------------------------------------------------

    1        June 1        185.2           27.0S               8.8       Onset of Storm
    2        June 8        189.2           19.0S               7.8       1st UATM Detection
    3        June 12       191.6           16.0S               7.4       Growth Phase
    4        June 16       194.0           13.0S               7.1       Growth Phase
    5        June 20       196.0           10.0S               6.6       PEDE Declared
    6        June 27       200.4            5.0S               6.0       Periapsis to Nightside
    7        July 7-10     207-208          4.0N               5.0       Peak of PEDE
    8        August 15     230.5           27.0N               2.0       Early Decay Phase
    9        August 30     240.6           45.0N              23.0       Mid Decay Phase
 	
*****************************************************************************************

MGITM Results are presented on a regular GEO grid (Longitude-Latitude-Altitude):
-------------------------------------------------------------------------
LON (72 elements) =   2.5 to 357.5 by 5.0 degree interval (fastest index)
LAT (36 elements) = -87.5 to +87.5 by 5.0 degree interval
ALT (62 elements) = 98.75 to 251.25 km by 2.5 km interval  (slowest index)

                    where

LON (2.5 to 180 to 357.5E) corresponds to SLT = 12 to 24 to 12
(We have selected the proper UT for each dataset for this match)

Fields (18):
-- Temperatures             : Tn, Ti, Te
   (neutral, ion, electron)
-- Major neutral densites   : [CO2], [O], [N2], [CO], [O2], [Ar]
-- Major plasma densities   : [O2+], [O+], [CO2+], [Ne]
   (dayside only, best in PCE region below 200 km)
-- 3-component neutral winds: Un, Vn, Wn
-- Pressure (total)         : P
-- Solar Zenith Angle       : SZA

Units  = All Temperatures (K),  All densities (#/m3), 3-component winds (m/s),
         Pressure (pascals), SZA (degrees)

File Nomenclature:
------------------------------
PEDE2.MGITM.YYMMDD.utXX.userdetic.dat

YY = last 2-digits of year
MM = 2-digit month
DD = 2-digit day of month
XX = Universal Time (on Earth): 2-digit integral hours
MonthYear = PEDE2 Interval

e.g. PEDE2.MGITM.160922.ut20.userdetic.dat
YY = 16
MM = 09
DD = 22
XX = 20

18-Files in the respository for downloading:
 ----------------------------------------------------------------------------------
PEDE2.MGITM.180530.UT07.userdetic.dat
README.30MAY2018.DATACUBE.txt

PEDE2.MGITM.180607.UT13.userdetic.dat
README.07JUNE2018.DATACUBE.txt

PEDE2.MGITM.180611.UT16.userdetic.dat
README.11JUNE2018.DATACUBE.txt

PEDE2.MGITM.180615.UT18.userdetic.dat
README.15JUNE2018.DATACUBE.txt

PEDE2.MGITM.180619.UT21.userdetic.dat
README.19JUNE2018.DATACUBE.txt

PEDE2.MGITM.180626.UT01.userdetic.dat
README.26JUNE2018.DATACUBE.txt

PEDE2.MGITM.180709.UT09.userdetic.dat
README.09JULY2018.DATACUBE.txt

PEDE2I.MGITM.180814.UT08.userdetic.dat
README.14AUG2018.DATACUBE.txt

PEDE2I.MGITM.180830.UT19.userdetic.dat
README.30AUG2018.DATACUBE.txt


FISM-Mars daily averaged solar EUV-UV fluxes (1-195 nm) used based upon MAVEN 
Extreme Ultraviolet Monitor (EUVM) instrument: Thiemann et al. (2017).
-------------------------------------------------------------------------------------
Level 3 EUVM daily products used: v11_r04 (all PEDE intervals)


*****************************************************************************************

Specific Key References pertaining to MGITM Simulations plus MAVEN NGIMS and IUVS Datasets:
--------------------------------------------------------------------------------------
Bougher et al. (2015), J. Geophys. Res., 120, 311-342, doi:10.1002/2014JE004715.
Bougher et al. (2015), Space Sci. Reviews, 195, 423-456, doi:10.1007/s11214-014-0053-7.
Bougher et al. (2017), J. Geophys. Res., 122, 1296-1313, doi:10.1002/2016JA023454.
Thiemann et al. (2017), J. Geophys. Res., 122, 2748-2767. doi:10.1002/2016JA023512.
Roeten et al.  (2019), J. Geophys. Res., XXX, YYYY-YYYY. doi:
Jain et al.    (2019), Geophys. Res. Lett., XXX, YYYY-YYYY. doi:
Elrod et al.   (2019), Geophys. Res. Lett., XXX, YYYY-YYYY. doi:

Citation for this dataset:
-------------------------
Bougher, S.W., Roeten, K.J.,Sharrar, R. (2019). Mars Thermospheric Responses to a Global Dust Storm (PEDE-2018): 
Mars Global Ionosphere-Thermosphere Model (M-GITM) Simulated Datasets for Comparison to MAVEN 
Spacecraft Measurements [Data set]. University of Michigan Deep Blue Data Repository. 
https://doi.org/xxxxxx

*****************************************************************************************
