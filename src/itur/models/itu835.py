# -*- coding: utf-8 -*-
import numpy as np
from iturutils import prepare_input_array, prepare_output_array,\
                      prepare_quantity
from astropy import units as u

class __ITU835():
    """Reference Standard Atmospheres

    Available versions:
    * P.835-5 (02/12) (Current version)

    Not available versions:
    * P.835-1 (08/94) (Superseded)
    * P.835-2 (08/97) (Superseded)
    * P.835-3 (10/99) (Superseded)
    * P.835-4 (03/05) (Superseded)

    The procedures to compute the reference standard atmosphere parameters
    pressented in these versions are identical to those included in version
    ITU_T P.835-5. Version 3 includes a dataset with vertical profiles for
    353 locations over the world using 10 years of radiosonde observations
    . Version 4 includes another dataset with monthly vertical profiles worldwide
    (grid of 1.5 by 1.5 deg). None of these are currently implemente but TODO
    work.
    """
    # This is an abstract class that contains an instance to a version of the
    # ITU-R P.835 recommendation.
    def __init__(self, version = 5):
        if version == 5:
            self.instance = _ITU835_5()
        else:
            raise ValueError('Version ' + str(version) + ' is not implemented'+
            ' for the ITU-R P.835 model.')

    @property
    def __version__(self):
        return self.instance.__version__

    def temperature(self, lat, h, season='summer'):
        #
        return self.instance.temperature(lat, h, season)

    def pressure(self, lat, h, season='summer'):
        return self.instance.pressure(lat, h, season)

    def water_vapour_density(self, lat, h, season='summer'):
        return self.instance.water_vapour_density(lat, h, season)

    def standard_temperature(self, h,  T_0):
        return self.instance.standard_temperature(h, T_0)

    def standard_pressure(self, h, T_0, P_0):
        return self.instance.standard_pressure(h, T_0, P_0)

    def standard_water_vapour_density(self, h, h_0, rho_0):
        return self.instance.standard_water_vapour_density(h, h_0, rho_0)

    def standard_water_vapour_pressure(self, h, h_0, rho_0):
        return self.instance.standard_water_vapour_pressure(h, h_0, rho_0)


class _ITU835_5():

    def __init__(self):
        self.__version__ = 6
        self.year = 2012
        self.month = 2
        self.link = 'https://www.itu.int/rec/R-REC-P.835-5-201202-I/en'


    def standard_temperature(self, h,  T_0=288.15):
        """

        """
        H = np.array([0, 11, 20, 32, 47, 51, 71, 85])
        T = np.array([0, -65, -65, -53, -11, -11, -67, -95]) + T_0

        return np.interp(h, H, T)

    def standard_pressure(self, h, T_0=288.15,  P_0=1013.25):
        """

        """
        H = [0, 11, 20, 32, 47, 51, 71, 85]
        L = [-6.5, 0, 1, 2.8, 0, -2.8, -2]
        T = np.array([0, -65, -65, -53, -11, -11, -67, -95]) + T_0

        num_splits = np.minimum(np.array(np.searchsorted(H, h)),7)
        if not hasattr(num_splits, '__iter__'):
            num_splits = list([num_splits])

        ret = np.ones_like(num_splits)*P_0
        for ret_i, n in enumerate(num_splits):
            P = np.zeros((n + 1))
            P[0] = P_0
            for i in range(n):
                h_p = H[ret_i] if i == (n - 1) else H[i+1]
                if L[i] != 0:
                    P[i+1] = P[i]*(T[i]/(T[i] + L[i]*(h_p - H[i])))**(34.163/L[i])
                else:
                    P[i+1] = P[i]*np.exp( -34.162*(h_p - H[i])/T[i])

            ret[ret_i] = P[-1]

        return ret

    def standard_water_vapour_density(self, h, h_0=2, rho_0=7.5):
        """

        """
        return rho_0 * np.exp(-h/h_0)

    def standard_water_vapour_pressure(self, h, h_0, rho_0):
        """

        """
        rho_h =self.standard_water_vapour_density(h, h_0, rho_0)
        T_h = self.standard_temperature(h)
        return rho_h * T_h / 216.7

    ## Low latitude standard atmosphere functions  (Section ITU-R P.835-5-2) ##
    def low_latitude_temperature(self, h):
        """Section 2 of Recommendation ITU-R P.835
        """
        return  np.where( ( 0 <= h) & (h < 17), 300.4222 - 6.3533 *h + 0.005886*h**2,
                np.where( (17 <= h) & (h < 47), 194 + (h - 17) * 2.533,
                np.where( (47 <= h) & (h < 52), 270,
                np.where( (52 <= h) & (h < 80), 270 - (h - 52)*3.0714,
                np.where( (80 <= h) & (h <= 100), 184, np.nan )))))

    def low_latitude_pressure(self, h):
        """Section 2 of Recommendation ITU-R P.835
        """

        P10 = self.standard_pressure(10)
        P72 = self.standard_pressure(72)
        return np.where( (0 <= h) & (h <= 10), 1012.0306 - 109.0338 * h + 3.6316 * h**2,
               np.where( (10 < h) & (h <= 72), P10 * np.exp( -0.147 * (h - 10)),
               np.where( (72 < h) & (h <= 100), P72 * np.exp( -0.165 * (h - 72)),
                        np.nan)))

    def low_latitude_water_vapour(self, h):
        """Section 3.1 of Recommendation ITU-R P.835
        """
        return np.where( (0 <= h) & (h <= 15), 19.6542* np.exp( - 0.2313  * h -
                0.1122 * h**2 + 0.01351 * h**3 - 0.0005923 * h**4), 0)

    ## High latitude standard atmosphere functions  (Section ITU-R P.835-5-2) ##
    def mid_latitude_temperature_summer(self, h):
        """Section 4.1 of Recommendation ITU-R P.835
        """
        return  np.where( ( 0 <= h) & (h < 10), 286.8374 - 4.7805 *h - 0.1402 *h**2,
                np.where( (10 <= h) & (h < 23), 225,
                np.where( (23 <= h) & (h < 48), 225 * np.exp((h -23) * 0.008317),
                np.where( (48 <= h) & (h < 53), 277,
                np.where( (53 <= h) & (h < 79), 277 - (h - 53) * 4.0769,
                np.where( (79 <= h) & (h <= 100), 171, np.nan ))))))

    def mid_latitude_pressure_summer(self, h):
        """Section 4.1 of Recommendation ITU-R P.835
        """
        P10 = self.standard_pressure(10)
        P72 = self.standard_pressure(72)
        return np.where( (0 <= h) & (h <= 10), 1008.0278 - 113.2494 * h + 3.9408 * h**2,
               np.where( (10 < h) & (h <= 72), P10 * np.exp( -0.140 * (h - 10)),
               np.where( (72 < h) & (h <= 100), P72 * np.exp( -0.165 * (h - 72)), np.nan)))

    def mid_latitude_water_vapour_summer(self, h):
        """Section 4.1 of Recommendation ITU-R P.835
        """
        return np.where( (0 <= h) & (h <= 15), 8.988* np.exp( - 0.3614  * h -
                0.005402 * h**2 - 0.001955 * h**3), 0)

    def mid_latitude_temperature_winter(self, h):
        """Section 4.2 of Recommendation ITU-R P.835
        """
        return  np.where( ( 0 <= h) & (h < 8.5), 257.4345 + 2.3474 *h - 1.5479 *h**2 + 0.08473 * h**3,
                np.where( (8.5 <= h) & (h < 30), 217.5,
                np.where( (30 <= h) & (h < 50), 217.5 + (h -30) * 2.125,
                np.where( (50 <= h) & (h < 54), 260,
                np.where( (54 <= h) & (h <= 100), 260 - (h - 54) * 1.667),
                        np.nan ))))

    def mid_latitude_pressure_winter(self, h):
        """Section 4.2 of Recommendation ITU-R P.835
        """
        P10 = self.standard_pressure(10)
        P72 = self.standard_pressure(72)
        return np.where( (0 <= h) & (h <= 10), 1010.8828 - 122.2411 * h + 4.554 * h**2,
               np.where( (10 < h) & (h <= 72), P10 * np.exp( -0.147 * (h - 10)),
               np.where( (72 < h) & (h <= 100), P72 * np.exp( -0.150 * (h - 72)), np.nan)))

    def mid_latitude_water_vapour_winter(self, h):
        """Section 4.2 of Recommendation ITU-R P.835
        """
        return np.where( (0 <= h) & (h <= 10), 1.2319 * np.exp( 0.07481  * h -
                0.0981 * h**2 + 0.00281 * h**3), 0)

    ## Mid latitude standard atmosphere functions  (Section ITU-R P.835-5-2) ##
    def high_latitude_temperature_summer(self, h):
        """Section 3.1 of Recommendation ITU-R P.835
        """
        return  np.where( ( 0 <= h) & (h < 13), 294.9838 - 5.2159 *h - 9.07109 *h**2,
                np.where( (13 <= h) & (h < 17), 215,
                np.where( (17 <= h) & (h < 47), 215 * np.exp((h -17) * 0.008128),
                np.where( (47 <= h) & (h < 53), 275,
                np.where( (53 <= h) & (h < 80), 275 + 20*(1 - np.exp((h - 53)*0.06)),
                np.where( (80 <= h) & (h <= 100), 175, np.nan ))))))

    def high_latitude_pressure_summer(self, h):
        """Section 3.1 of Recommendation ITU-R P.835
        """
        P10 = self.standard_pressure(10)
        P72 = self.standard_pressure(72)
        return np.where( (0 <= h) & (h <= 10), 1012.8186 - 111.5569 * h + 3.8646 * h**2,
               np.where( (10 < h) & (h <= 72), P10 * np.exp( -0.147 * (h - 10)),
               np.where( (72 < h) & (h <= 100), P72 * np.exp( -0.165 * (h - 72)), np.nan)))

    def high_latitude_water_vapour_summer(self, h):
        """Section 3.1 of Recommendation ITU-R P.835
        """
        return np.where( (0 <= h) & (h <= 15), 14.3542* np.exp( - 0.4174  * h -
                0.02290 * h**2 + 0.001007 * h**3), 0)

    def high_latitude_temperature_winter(self, h):
        """Section 3.2 of Recommendation ITU-R P.835
        """
        return  np.where( ( 0 <= h) & (h < 10), 272.7241 - 3.6217 *h - 0.1759 *h**2,
                np.where( (10 <= h) & (h < 33), 218,
                np.where( (33 <= h) & (h < 47), 218 + (h -33) * 3.3571,
                np.where( (47 <= h) & (h < 53), 265,
                np.where( (53 <= h) & (h < 80), 265 - (h - 53)*2.0370),
                np.where( (80 <= h) & (h <= 100), 210, np.nan )))))

    def high_latitude_pressure_winter(self, h):
        """Section 3.2 of Recommendation ITU-R P.835
        """
        P10 = self.standard_pressure(10)
        P72 = self.standard_pressure(72)
        return np.where( (0 <= h) & (h <= 10), 1018.8627 - 124.2954 * h + 4.8307 * h**2,
               np.where( (10 < h) & (h <= 72), P10 * np.exp( -0.147 * (h - 10)),
               np.where( (72 < h) & (h <= 100), P72 * np.exp( -0.155 * (h - 72)), np.nan)))

    def high_latitude_water_vapour_winter(self, h):
        """Section 3.2 of Recommendation ITU-R P.835
        """
        return np.where( 0 <= h & h <= 10, 3.4742* np.exp( - 0.2697  * h -
                0.03604 * h**2 + 0.0004489 * h**3), 0)

    def temperature(self, lat, h, season='summer'):
       """ Section 2 of Recommendation ITU-R P.835
       """
       if season=='summer':
           return np.where(np.abs(lat) < 22, self.low_latitude_temperature(h),
           np.where(np.abs(lat) < 45, self.mid_latitude_temperature_summer(h),
                    self.high_latitude_temperature_summer(h)))
       else:
           return np.where(np.abs(lat) < 22, self.low_latitude_temperature(h),
           np.where(np.abs(lat) < 45, self.mid_latitude_temperature_winter(h),
                    self.high_latitude_temperature_winter(h)))

    def pressure(self, lat, h, season='summer'):
       """ Section 2 of Recommendation ITU-R P.835
       """
       if season=='summer':
           return np.where(np.abs(lat) < 22, self.low_latitude_pressure(h),
           np.where(np.abs(lat) < 45, self.mid_latitude_pressure_summer(h),
                    self.high_latitude_pressure_summer(h)))
       else:
           return np.where(np.abs(lat) < 22, self.low_latitude_pressure(h),
           np.where(np.abs(lat) < 45, self.mid_latitude_pressure_winter(h),
                    self.high_latitude_pressure_winter(h)))

    def water_vapour_density(self, lat, h, season='summer'):
       """ Section 2 of Recommendation ITU-R P.835
       """
       if season=='summer':
           return np.where(np.abs(lat) < 22, self.low_latitude_water_vapour(h),
           np.where(np.abs(lat) < 45, self.mid_latitude_water_vapour_summer(h),
                    self.high_latitude_water_vapour_summer(h)))
       else:
           return np.where(np.abs(lat) < 22, self.low_latitude_water_vapour(h),
           np.where(np.abs(lat) < 45, self.mid_latitude_water_vapour_winter(h),
                    self.high_latitude_water_vapour_winter(h)))



__model = __ITU835()

def change_version(new_version):
    """
    Change the version of the ITU-R P.835 recommendation currently being used.

    Parameters
    ----------
    new_version : int
        Number of the version to use.
        Valid values are:
        * P.835-1 (08/94) (Superseded)
        * P.835-2 (10/99) (Superseded)
        * P.835-3 (02/01) (Superseded)
        * P.835-4 (04/03) (Superseded)
        * P.835-5 (08/07) (Superseded)
        * P.835-6 (02/12) (Current version)
    """
    global __model
    __model = __ITU835(new_version)

def get_version():
    """
    Obtain the version of the ITU-R P.835 recommendation currently being used.
    """
    global __model
    return __model.__version__

def temperature(lat, h, season='summer'):
    """
    Method to determine the temperature as a function of altitude and latitude,
    for calculating gaseous attenuation along an Earth-space path. This method
    is recommended when more reliable local data are not available.

    Parameters
    ----------
    lat : number, sequence, or numpy.ndarray
        Latitudes of the receiver points
    h : number or Quantity
        Height (km)
    season : string
        Season of the year (available values, 'summer', and 'winter').
        Default 'summer'

    Returns
    -------
    T: Quantity
        Temperature (K)

    References:
    -----------
    [1] Reference Standard Atmospheres
    https://www.itu.int/rec/R-REC-P.835/en

    """
    global __model
    type_output = type(lat)
    lat = prepare_input_array(lat)
    h = prepare_quantity(h, u.km, 'Height')
    val = __model.temperature(lat, h, season)
    return prepare_output_array(val, type_output)*u.Kelvin

def pressure(lat, h, season='summer'):
    """
    Method to determine the pressure as a function of altitude and latitude,
    for calculating gaseous attenuation along an Earth-space path.
    This method is recommended when more reliable local data are not available.

    Parameters
    ----------
    lat : number, sequence, or numpy.ndarray
        Latitudes of the receiver points
    h : number or Quantity
        Height (km)
    season : string
        Season of the year (available values, 'summer', and 'winter').
        Default 'summer'

    Returns
    -------
    P: Quantity
        Pressure (hPa)

    References:
    -----------
    [1] Reference Standard Atmospheres
    https://www.itu.int/rec/R-REC-P.835/en
    """
    global __model
    type_output = type(lat)
    lat = prepare_input_array(lat)
    h = prepare_quantity(h, u.km, 'Height')
    val = __model.pressure(lat, h, season)
    return prepare_output_array(val, type_output)*u.hPa


def water_vapour_density(lat, h, season='summer'):
    """
    Method to determine the water-vapour density as a
    function of altitude and latitude, for calculating gaseous attenuation along
    an Earth-space path. This method is recommended when more reliable
    local data are not available.

    Parameters
    ----------
    lat : number, sequence, or numpy.ndarray
        Latitudes of the receiver points
    h : number or Quantity
        Height (km)
    season : string
        Season of the year (available values, 'summer', and 'winter').
        Default 'summer'

    Returns
    -------
    rho: Quantity
        Water vapour density (g/m^3)

    References:
    -----------
    [1] Reference Standard Atmospheres
    https://www.itu.int/rec/R-REC-P.835/en
    """
    global __model
    type_output = type(lat)
    lat = prepare_input_array(lat)
    h = prepare_quantity(h, u.km, 'Height')
    val = __model.water_vapour_density(lat, h, season)
    return prepare_output_array(val, type_output) * u.g/u.m**3

def standard_temperature(h,  T_0=288.15):
    """
    Method to compute the temperature of an standard atmosphere at
    a given height.

    The reference standard atmosphere is based on the United States Standard
    Atmosphere, 1976, in which the atmosphere is divided into seven successive
    layers showing linear variation with temperature.

    Parameters
    ----------
    h : number or Quantity
        Height (km)
    T_0 : number or Quantity
        Surface temperature (K)

    Returns
    -------
    T: Quantity
        Temperature (K)

    References:
    -----------
    [1] Reference Standard Atmospheres
    https://www.itu.int/rec/R-REC-P.835/en
    """
    global __model

    h = prepare_quantity(h, u.km, 'Height')
    T_0 = prepare_quantity(T_0, u.Kelvin, 'Surface temperature')
    return __model.standard_temperature(h, T_0)*u.Kelvin

def standard_pressure(h,  T_0=288.15, P_0=1013.25):
    """
    Method to compute the total atmopsheric pressure of an standard atmosphere at
    a given height.

    The reference standard atmosphere is based on the United States Standard
    Atmosphere, 1976, in which the atmosphere is divided into seven successive
    layers showing linear variation with temperature.

    Parameters
    ----------
    h : number or Quantity
        Height (km)
    T_0 : number or Quantity
        Surface temperature (K)
    P_0 : number or Quantity
        Surface pressure (hPa)

    Returns
    -------
    P: Quantity
        Pressure (hPa)

    References:
    -----------
    [1] Reference Standard Atmospheres
    https://www.itu.int/rec/R-REC-P.835/en
    """
    global __model

    h = prepare_quantity(h, u.km, 'Height')
    T_0 = prepare_quantity(T_0, u.Kelvin, 'Surface temperature')
    P_0 = prepare_quantity(P_0, u.hPa, 'Surface pressure')
    return __model.standard_pressure(h, T_0, P_0)*u.hPa

def standard_water_vapour_density(h, h_0=2, rho_0=7.5):
    """
    Method to compute the water vapour density of an standard atmosphere at
    a given height.

    The reference standard atmosphere is based on the United States Standard
    Atmosphere, 1976, in which the atmosphere is divided into seven successive
    layers showing linear variation with temperature.

    Parameters
    ----------
    h : number or Quantity
        Height (km)
    h_0 : number or Quantity
        Scale height (km)
    rho_0 : number or Quantity
        Surface water vapour density (g/m^3)

    Returns
    -------
    rho: Quantity
        Water vapour density (g/m^3)

    References:
    -----------
    [1] Reference Standard Atmospheres
    https://www.itu.int/rec/R-REC-P.835/en
    """
    global __model

    h = prepare_quantity(h, u.km, 'Height')
    h_0 = prepare_quantity(h_0, u.km, 'Scale height')
    rho_0 = prepare_quantity(rho_0, u.g/u.m**3, 'Surface water vapour density')
    return __model.standard_water_vapour_density(h, h_0, rho_0)*u.g/u.m**3

def standard_water_vapour_pressure(h, h_0=2, rho_0=7.5):
    """
    Method to compute the water vapour pressure of an standard atmosphere at
    a given height.

    The reference standard atmosphere is based on the United States Standard
    Atmosphere, 1976, in which the atmosphere is divided into seven successive
    layers showing linear variation with temperature.

    Parameters
    ----------
    h : number or Quantity
        Height (km)
    h_0 : number or Quantity
        Scale height (km)
    rho_0 : number or Quantity
        Surface water vapour density (g/m^3)

    Returns
    -------
    e: Quantity
        Water vapour pressure (hPa)

    References:
    -----------
    [1] Reference Standard Atmospheres
    https://www.itu.int/rec/R-REC-P.835/en
    """
    global __model

    h = prepare_quantity(h, u.km, 'Height')
    h_0 = prepare_quantity(h_0, u.km, 'Scale height')
    rho_0 = prepare_quantity(rho_0, u.g/u.m**3, 'Surface water vapour density')
    return __model.standard_water_vapour_pressure(h, h_0, rho_0)*u.hPa