import math

import numpy as np
import pytest

from earhart import coordinates as c
from earhart.coordinates import LatLon

A_WGS84 = 6378137.0


def test_nm_definition_exact():
    assert c.nm_to_m(1.0) == 1852.0
    assert c.m_to_nm(1852.0) == 1.0


def test_one_degree_longitude_on_equator():
    # arc length = a * dlon (radians) on the equator
    d = c.distance_nm(LatLon(0, 0), LatLon(0, 1))
    assert d * 1852.0 == pytest.approx(A_WGS84 * math.pi / 180, abs=1e-3)


def test_pole_to_equator_meridian_quadrant():
    # WGS84 meridian quadrant: 10,001,965.729 m
    d = c.distance_nm(LatLon(0, 10), LatLon(90, 10))
    assert d * 1852.0 == pytest.approx(10_001_965.729, abs=0.01)


def test_geodesy_published_vincenty_case():
    # Geoscience Australia: Flinders Peninsula -> Buninyong (GRS80≈WGS84 here)
    p1 = LatLon(c.dms_to_decimal(37, 57, 3.72030, "S"), c.dms_to_decimal(144, 25, 29.52440, "E"))
    p2 = LatLon(c.dms_to_decimal(37, 39, 10.15610, "S"), c.dms_to_decimal(143, 55, 35.38390, "E"))
    az, back, nm = c.inverse(p1, p2)
    assert nm * 1852.0 == pytest.approx(54972.271, abs=0.01)
    assert az == pytest.approx(306 + 52 / 60 + 5.37 / 3600, abs=1e-5)


def test_forward_inverse_roundtrip():
    rng = np.random.default_rng(0)
    for _ in range(50):
        o = LatLon(rng.uniform(-60, 60), rng.uniform(-180, 180))
        az, dist = rng.uniform(0, 360), rng.uniform(1, 2000)
        dest = c.forward(o, az, dist)
        az2, _, d2 = c.inverse(o, dest)
        assert d2 == pytest.approx(dist, abs=1e-6)
        assert (az2 - az + 180) % 360 - 180 == pytest.approx(0, abs=1e-6)


def test_antimeridian_wrap():
    # Route of interest crosses 180°; distance must not take the long way round.
    d = c.distance_nm(LatLon(0, 179.5), LatLon(0, -179.5))
    assert d == pytest.approx(60.0, rel=0.01)
    assert c.normalize_lon(-179.5) == -179.5
    assert LatLon(0, 181).lon == -179.0
    assert LatLon(0, 180).lon == -180.0


def test_vectorised_matches_scalar():
    lat, lon = np.array([1.0, -5.0]), np.array([170.0, -179.0])
    az, dist = np.array([90.0, 45.0]), np.array([100.0, 250.0])
    la, lo = c.forward_array(lat, lon, az, dist)
    for i in range(2):
        s = c.forward(LatLon(lat[i], lon[i]), az[i], dist[i])
        assert (la[i], lo[i]) == pytest.approx(s.as_tuple(), abs=1e-9)
    a2, d2 = c.inverse_array(lat, lon, la, lo)
    assert d2 == pytest.approx(dist, abs=1e-6)


def test_route_endpoints_and_monotonic():
    a, b = LatLon(-6.7, 147.0), LatLon(0.8, -176.6)
    pts = c.geodesic_route(a, b, 20)
    assert len(pts) == 22 and pts[0] == a
    assert pts[-1].lat == pytest.approx(b.lat) and pts[-1].lon == pytest.approx(b.lon)
    total = c.distance_nm(a, b)
    legs = sum(c.distance_nm(p, q) for p, q in zip(pts, pts[1:]))
    assert legs == pytest.approx(total, rel=1e-9)
    f = c.route_point_at_fraction(a, b, 0.5)
    assert c.distance_nm(a, f) == pytest.approx(total / 2, rel=1e-9)


def test_lop_reciprocal():
    assert c.lop_reciprocal(157) == 337
    assert c.lop_reciprocal(337) == 157


def test_lop_passes_through_point_and_has_azimuth():
    p = LatLon(0.5, -176.0)
    line = c.lop_through(p, 157, half_length_nm=100, n_points=21)
    assert line[10].lat == pytest.approx(p.lat, abs=1e-9)
    assert line[10].lon == pytest.approx(p.lon, abs=1e-9)
    assert c.bearing_deg(line[10], line[-1]) == pytest.approx(157, abs=0.05)
    assert c.bearing_deg(line[10], line[0]) == pytest.approx(337, abs=0.05)
    assert c.distance_nm(line[0], line[-1]) == pytest.approx(200, rel=1e-6)


def test_lop_offset_is_perpendicular_and_signed():
    p = LatLon(0.0, -176.0)
    for off in (-15.0, 7.5):
        line = c.lop_through(p, 157, offset_nm=off, n_points=3)
        ct = c.cross_track_nm(p, line[1], 157)
        # point is |off| from displaced line; sign: p is left (neg) of a line moved right
        assert ct == pytest.approx(-off, abs=0.05)
        assert c.along_track_nm(p, line[1], 157) == pytest.approx(0, abs=0.05)


def test_lop_angle_error_rotates_about_point_not_translates():
    p = LatLon(0.0, -176.0)
    line = c.lop_through(p, 157, angle_error_deg=3.0, half_length_nm=100, n_points=3)
    assert line[1].lat == pytest.approx(p.lat, abs=1e-9)  # pivot unchanged
    assert c.bearing_deg(line[1], line[2]) == pytest.approx(160, abs=0.05)
    # far end displaced ~ 100*sin(3°) ≈ 5.2 nm from the unrotated line
    ct = c.cross_track_nm(line[2], p, 157)
    assert ct == pytest.approx(100 * math.sin(math.radians(3)), rel=0.01)


def test_cross_track_along_track_decomposition():
    o = LatLon(0, -176)
    pt = c.forward(o, 90, 50)
    ct, at = c.cross_track_nm(pt, o, 157), c.along_track_nm(pt, o, 157)
    assert math.hypot(ct, at) == pytest.approx(50, rel=1e-3)


def test_lop_bad_inputs():
    with pytest.raises(ValueError):
        c.lop_through(LatLon(0, 0), 157, n_points=1)
    with pytest.raises(ValueError):
        c.perpendicular_bearing(157, "up")


@pytest.mark.parametrize(
    "text,expected",
    [("0°48'N", 0.8), ("176 38 E", 176 + 38 / 60), ("37°57'03.72\"S", -(37 + 57 / 60 + 3.72 / 3600)), ("10W", -10.0)],
)
def test_parse_dms(text, expected):
    assert c.parse_dms(text) == pytest.approx(expected)


def test_parse_dms_rejects_garbage():
    for bad in ("", "abc", "12°70'N", "5 5 5 5 N"):
        with pytest.raises(ValueError):
            c.parse_dms(bad)


def test_dms_roundtrip_and_carry():
    for v, is_lat in [(-37.95103341666667, True), (144.42486788888888, False), (0.0, True)]:
        d, m, s, h = c.decimal_to_dms(v, is_lat)
        assert c.dms_to_decimal(d, m, s, h) == pytest.approx(v, abs=1e-9)
    assert c.format_dms(0.99999999999, True) == "1°00'00.0\"N"
    assert c.format_dms(-37.5, True) == "37°30'00.0\"S"


def test_latlon_validation():
    with pytest.raises(ValueError):
        LatLon(91, 0)
