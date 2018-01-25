# Import specific functions that are available under the main itur module
from itur.models.itu618 import rain_attenuation, scintillation_attenuation
from itur.models.itu676 import gaseous_attenuation_slant_path,\
    gaseous_attenuation_inclined_path,\
    gaseous_attenuation_terrestrial_path
from itur.models.itu835 import pressure
from itur.models.itu836 import surface_water_vapour_density
from itur.models.itu840 import cloud_attenuation
from itur.models.itu1510 import surface_mean_temperature
from itur.models.itu1511 import topographic_altitude

import itur.models

import numpy as np
import warnings
import astropy.units as u

def atmospheric_attenuation_slant_path(
        lat, lon, el, f, p, D, hs=None, rho=None, R001=None, eta=0.5, T=None,
        H=None, P=None, hL=1e3, Ls=None, tau=45, mode='approx',
        return_contributions=False, include_rain=True, include_gas=True,
        include_scintillation=True, include_clouds=True):
    """
    """
    if p < 0.001 or p > 50:
        warnings.warn(
            RuntimeWarning(
                'The method to compute the total '
                'atmospheric attenuation in recommendation ITU-P 618-12 '
                'is only recommended for unavailabilities (p) between '
                '0.001 % and 50 %'))

    # Estimate the ground station altitude
    if hs is None:
        hs = topographic_altitude(lat, lon)

    # Surface mean temperature
    if T is None:
        T = surface_mean_temperature(lat, lon)

    # Estimate the surface Pressure
    if P is None:
        P = pressure(lat, hs)

    # Estimate the surface water vapour density
    if rho is None:
        rho = surface_water_vapour_density(lat, lon, p, hs)

    # Compute the attenuation components
    if include_rain:
        Ar = rain_attenuation(lat, lon, f, el, hs, p, R001, tau, Ls)
    else:
        Ar = 0 * u.dB

    # This takes account of the fact that a large part of the cloud attenuation
    # and gaseous attenuation is already included in the rain attenuation
    # prediction for time percentages below 1%. Eq. 64 and Eq. 65 in
    # Recommendation ITU 618-12
    p_c_g = max(1, p)

    if include_gas:
        Ag = gaseous_attenuation_slant_path(f, el, rho, P, T, mode)
    else:
        Ag = 0 * u.dB

    if include_clouds:
        Ac = cloud_attenuation(lat, lon, el, f, p_c_g)
    else:
        Ac = 0 * u.dB

    if include_scintillation:
        As = scintillation_attenuation(lat, lon, f, el, p, D, eta,
                                       T, H, P, hL)
    else:
        As = 0 * u.dB

    # Compute the total attenuation according to
    A = Ag + np.sqrt((Ar + Ac)**2 + As**2)

    if return_contributions:
        return Ag, Ac, Ar, As, A
    else:
        return A