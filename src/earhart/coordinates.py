"""WGS84 geodesy primitives: distances, bearings, routes and lines of position.

Conventions
-----------
* Latitude/longitude are decimal degrees, north/east positive, WGS84.
* Azimuths/bearings are degrees clockwise from north, normalised to [0, 360).
* Distances are metres internally; nautical miles use the exact international
  definition (1 nm = 1852 m). Statute miles are deliberately not provided:
  1937 sources mix units, and unit ambiguity must be handled at the evidence
  layer, not silently here.
* Azimuths here are *true* unless a caller says otherwise. Whether a historical
  bearing (e.g. "157 337") is true or magnetic is a research question, not a
  property of this module; convert explicitly before calling.
* No station coordinates (Lae, Howland, ...) are defined here. They are
  evidence-registry values and must be loaded with provenance.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

import numpy as np
from pyproj import Geod

GEOD = Geod(ellps="WGS84")
METRES_PER_NM = 1852.0


@dataclass(frozen=True, slots=True)
class LatLon:
    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not -90.0 <= self.lat <= 90.0:
            raise ValueError(f"latitude out of range: {self.lat}")
        if not math.isfinite(self.lon):
            raise ValueError(f"longitude not finite: {self.lon}")
        object.__setattr__(self, "lon", normalize_lon(self.lon))

    def as_tuple(self) -> tuple[float, float]:
        return (self.lat, self.lon)


def normalize_lon(lon: float) -> float:
    """Wrap longitude to [-180, 180). Matters here: the route crosses 180°."""
    return (lon + 180.0) % 360.0 - 180.0


def normalize_bearing(brg: float) -> float:
    return brg % 360.0


def m_to_nm(metres: float | np.ndarray) -> float | np.ndarray:
    return metres / METRES_PER_NM


def nm_to_m(nm: float | np.ndarray) -> float | np.ndarray:
    return nm * METRES_PER_NM


# --- inverse / forward problems -------------------------------------------------


def inverse(a: LatLon, b: LatLon) -> tuple[float, float, float]:
    """Return (forward_azimuth_deg, back_azimuth_deg, distance_nm) from a to b."""
    az12, az21, dist_m = GEOD.inv(a.lon, a.lat, b.lon, b.lat)
    return normalize_bearing(az12), normalize_bearing(az21), dist_m / METRES_PER_NM


def distance_nm(a: LatLon, b: LatLon) -> float:
    return inverse(a, b)[2]


def bearing_deg(a: LatLon, b: LatLon) -> float:
    """Initial true bearing from a to b."""
    return inverse(a, b)[0]


def forward(origin: LatLon, azimuth_deg: float, dist_nm: float) -> LatLon:
    """Destination reached from origin along a geodesic."""
    lon, lat, _ = GEOD.fwd(origin.lon, origin.lat, azimuth_deg, dist_nm * METRES_PER_NM)
    return LatLon(lat, lon)


def forward_array(
    lat: np.ndarray, lon: np.ndarray, azimuth_deg: np.ndarray, dist_nm: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised `forward`, for Monte Carlo use. Returns (lat, lon) arrays."""
    lon2, lat2, _ = GEOD.fwd(lon, lat, azimuth_deg, np.asarray(dist_nm) * METRES_PER_NM)
    return np.asarray(lat2), (np.asarray(lon2) + 180.0) % 360.0 - 180.0


def inverse_array(
    lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised inverse. Returns (forward_azimuth_deg, distance_nm)."""
    az, _, d = GEOD.inv(lon1, lat1, lon2, lat2)
    return np.asarray(az) % 360.0, np.asarray(d) / METRES_PER_NM


# --- routes ------------------------------------------------------------------------


def geodesic_route(a: LatLon, b: LatLon, n_intermediate: int = 99) -> list[LatLon]:
    """Points along the WGS84 geodesic a→b, endpoints included.

    The WGS84 geodesic is the ellipsoidal analogue of the great circle. It
    differs from a spherical great circle by up to ~0.2% in length; a 1937
    navigator would have used spherical or rhumb/Mercator methods. Compare
    against `rhumb_*` or a spherical model before attributing differences to
    navigation error.
    """
    if n_intermediate < 0:
        raise ValueError("n_intermediate must be >= 0")
    mid = GEOD.npts(a.lon, a.lat, b.lon, b.lat, n_intermediate) if n_intermediate else []
    return [a, *(LatLon(lat, lon) for lon, lat in mid), b]


def route_point_at_fraction(a: LatLon, b: LatLon, fraction: float) -> LatLon:
    az, _, dist = inverse(a, b)
    return forward(a, az, dist * fraction)


# --- lines of position ---------------------------------------------------------------


def perpendicular_bearing(lop_azimuth_deg: float, side: str = "right") -> float:
    """Bearing at 90° to the LOP, on its right or left when facing along it."""
    if side not in ("right", "left"):
        raise ValueError("side must be 'right' or 'left'")
    return normalize_bearing(lop_azimuth_deg + (90.0 if side == "right" else -90.0))


def lop_through(
    point: LatLon,
    azimuth_deg: float,
    half_length_nm: float = 300.0,
    n_points: int = 61,
    offset_nm: float = 0.0,
    offset_bearing_deg: float | None = None,
    angle_error_deg: float = 0.0,
) -> list[LatLon]:
    """Polyline of a line of position through `point`, ordered along `azimuth_deg`.

    Two error terms are kept separate on purpose:

    * `offset_nm` translates the whole line perpendicular to itself (the LOP is
      *displaced*; the observer's true position is still somewhere on a parallel
      line). Positive offset moves toward `offset_bearing_deg`, default the
      right-hand perpendicular of the LOP azimuth.
    * `angle_error_deg` rotates the line about `point` (orientation error).

    Neither describes where *along* the line the aircraft is; that is a
    separate position uncertainty modelled in the navigation module.
    """
    if n_points < 2:
        raise ValueError("n_points must be >= 2")
    centre = point
    if offset_nm:
        perp = (
            perpendicular_bearing(azimuth_deg)
            if offset_bearing_deg is None
            else normalize_bearing(offset_bearing_deg)
        )
        centre = forward(point, perp, offset_nm)
    az = normalize_bearing(azimuth_deg + angle_error_deg)
    out: list[LatLon] = []
    for s in np.linspace(-half_length_nm, half_length_nm, n_points):
        out.append(forward(centre, az, s) if s >= 0 else forward(centre, normalize_bearing(az + 180.0), -s))
    return out


def lop_reciprocal(azimuth_deg: float) -> float:
    """The other direction of the same line (157 <-> 337)."""
    return normalize_bearing(azimuth_deg + 180.0)


def cross_track_nm(point: LatLon, line_point: LatLon, line_azimuth_deg: float) -> float:
    """Signed perpendicular distance (nm) from `point` to the geodesic through
    `line_point` with initial azimuth `line_azimuth_deg`. Positive = right of line
    when facing along the azimuth.

    Uses a local azimuthal-equidistant projection centred on `line_point`;
    accurate for the few-hundred-nm scales used here, not for global distances.
    """
    az, _, d = inverse(line_point, point)
    return d * math.sin(math.radians(az - line_azimuth_deg))


def along_track_nm(point: LatLon, line_point: LatLon, line_azimuth_deg: float) -> float:
    """Signed distance (nm) along the line from `line_point` to the foot of `point`."""
    az, _, d = inverse(line_point, point)
    return d * math.cos(math.radians(az - line_azimuth_deg))


# --- text formats -----------------------------------------------------------------------

_DMS_RE = re.compile(
    r"""^\s*(?P<deg>\d+(?:\.\d+)?)\s*[°d\s]?\s*
        (?:(?P<min>\d+(?:\.\d+)?)\s*['′m\s]\s*)?
        (?:(?P<sec>\d+(?:\.\d+)?)\s*["″s]?\s*)?
        (?P<hem>[NSEWnsew])\s*$""",
    re.VERBOSE,
)


def dms_to_decimal(deg: float, minutes: float = 0.0, seconds: float = 0.0, hemisphere: str = "N") -> float:
    hemisphere = hemisphere.upper()
    if hemisphere not in "NSEW" or len(hemisphere) != 1:
        raise ValueError(f"bad hemisphere: {hemisphere!r}")
    if not (0 <= minutes < 60 and 0 <= seconds < 60):
        raise ValueError("minutes and seconds must be in [0, 60)")
    value = abs(deg) + minutes / 60.0 + seconds / 3600.0
    return -value if hemisphere in "SW" else value


def parse_dms(text: str) -> float:
    """Parse e.g. ``0°48'N``, ``176 38 E``, ``37°57'03.72"S`` to decimal degrees."""
    m = _DMS_RE.match(text)
    if not m:
        raise ValueError(f"cannot parse coordinate: {text!r}")
    return dms_to_decimal(
        float(m["deg"]), float(m["min"] or 0), float(m["sec"] or 0), m["hem"]
    )


def decimal_to_dms(value: float, is_lat: bool) -> tuple[int, int, float, str]:
    hem = ("N" if value >= 0 else "S") if is_lat else ("E" if value >= 0 else "W")
    v = abs(value)
    d = int(v)
    m = int((v - d) * 60)
    s = (v - d - m / 60.0) * 3600.0
    if s >= 60.0 - 1e-9:  # guard rounding carry
        s, m = 0.0, m + 1
    if m == 60:
        m, d = 0, d + 1
    return d, m, s, hem


def format_dms(value: float, is_lat: bool, seconds_places: int = 1) -> str:
    hem = ("N" if value >= 0 else "S") if is_lat else ("E" if value >= 0 else "W")
    scale = 10**seconds_places
    total = round(abs(value) * 3600 * scale)  # round once, so carries are exact
    d, rem = divmod(total, 3600 * scale)
    m, sec = divmod(rem, 60 * scale)
    return f"{d}°{m:02d}'{sec / scale:0{3 + seconds_places}.{seconds_places}f}\"{hem}"
