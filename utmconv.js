///
/// A UTM -> Lat/Long (or vice versa) converter adapted from the script used at 
///     http://www.uwgb.edu/dutchs/UsefulData/ConvertUTMNoOZ.HTM
/// I've taken the calculations portion of his script and turned it into a singleton
/// javascript object so that it is no longer dependent on the controls used on the page
/// to use this script, call setDatum with the index of the datum to be used and then
/// call the various conversion functions latLngToUtm(), utmToLatLng() or natoToLatLng(), utmToNato(), natoToUtm()
/// to convert between the various coordinate systems, hopefully accurately!
///
/// NOTE: no attempt is made to compensate for the irregular grid in the area around the southern coast of Norway and
/// Svalbard (zones 32V and 31X, 33X, 35X and 37X) because of this results returned for NATO coordinates for lat/lng or
/// UTM values located in these regions will not be correct.
///
var utmconv = {
    //
    // constants taken from or calculated from the datum
    //
    a: 0,   // equatorial radius in meters
    f: 0,   // polar flattening
    b: 0,   // polar radius in meters
    e: 0,   // eccentricity
    e0: 0,  // e'


    //
    // constants used in calculations
    //
    k: 1,
    k0: 0.9996,
    drad: Math.PI / 180,

    digraphLettersE: "ABCDEFGHJKLMNPQRSTUVWXYZ",
    digraphLettersN: "ABCDEFGHJKLMNPQRSTUV",
    digraphLettersAll: "ABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUVABCDEFGHJKLMNPQRSTUV",
    datumTable: [
        { eqRad: 6378137.0, flat: 298.2572236 },    // WGS 84
        { eqRad: 6378137.0, flat: 298.2572236 },    // NAD 83
        { eqRad: 6378137.0, flat: 298.2572215 },    // GRS 80
        { eqRad: 6378135.0, flat: 298.2597208 },    // WGS 72
        { eqRad: 6378160.0, flat: 298.2497323 },    // Austrailian 1965
        { eqRad: 6378245.0, flat: 298.2997381 },    // Krasovsky 1940
        { eqRad: 6378206.4, flat: 294.9786982 },    // North American 1927
        { eqRad: 6378388.0, flat: 296.9993621 },    // International 1924
        { eqRad: 6378388.0, flat: 296.9993621 },    // Hayford 1909
        { eqRad: 6378249.1, flat: 293.4660167 },    // Clarke 1880
        { eqRad: 6378206.4, flat: 294.9786982 },    // Clarke 1866
        { eqRad: 6377563.4, flat: 299.3247788 },    // Airy 1830
        { eqRad: 6377397.2, flat: 299.1527052 },    // Bessel 1841
        { eqRad: 6377276.3, flat: 300.8021499 }     // Everest 1830
    ],

    ///
    /// calculate constants used for doing conversions using a given map datum
    ///
    setDatum: function (index) {
        var datum = this.datumTable[index];
        this.a = datum.eqRad;
        this.f = 1 / datum.flat;
        this.b = this.a * (1 - this.f);   // polar radius
        this.e = Math.sqrt(1 - Math.pow(this.b, 2) / Math.pow(this.a, 2));
        this.e0 = this.e / Math.sqrt(1 - this.e);
    },

    ///
    /// convert a set of global UTM coordinates to lat/lng returned as follows
    ///
    /// { lat: y, lng: x }
    ///
    /// inputs:
    ///     x: easting
    ///     y: northing
    ///     utmz: utm zone
    ///     southern: bool indicating coords are in southern hemisphere
    ///
    utmToLatLng: function(x, y, utmz, southern) {
        var esq = (1 - (this.b / this.a) * (this.b / this.a));
        var e0sq = this.e * this.e / (1 - Math.pow(this.e, 2));
        var zcm = 3 + 6 * (utmz - 1) - 180;                         // Central meridian of zone
        var e1 = (1 - Math.sqrt(1 - Math.pow(this.e, 2))) / (1 + Math.sqrt(1 - Math.pow(this.e, 2)));
        var M0 = 0;
        var M = 0;

        if (!southern)
            M = M0 + y / this.k0;    // Arc length along standard meridian. 
        else
            M = M0 + (y - 10000000) / this.k;

        var mu = M / (this.a * (1 - esq * (1 / 4 + esq * (3 / 64 + 5 * esq / 256))));
        var phi1 = mu + e1 * (3 / 2 - 27 * e1 * e1 / 32) * Math.sin(2 * mu) + e1 * e1 * (21 / 16 - 55 * e1 * e1 / 32) * Math.sin(4 * mu);   //Footprint Latitude
        phi1 = phi1 + e1 * e1 * e1 * (Math.sin(6 * mu) * 151 / 96 + e1 * Math.sin(8 * mu) * 1097 / 512);
        var C1 = e0sq * Math.pow(Math.cos(phi1), 2);
        var T1 = Math.pow(Math.tan(phi1), 2);
        var N1 = this.a / Math.sqrt(1 - Math.pow(this.e * Math.sin(phi1), 2));
        var R1 = N1 * (1 - Math.pow(this.e, 2)) / (1 - Math.pow(this.e * Math.sin(phi1), 2));
        var D = (x - 500000) / (N1 * this.k0);
        var phi = (D * D) * (1 / 2 - D * D * (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * e0sq) / 24);
        phi = phi + Math.pow(D, 6) * (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 252 * e0sq - 3 * C1 * C1) / 720;
        phi = phi1 - (N1 * Math.tan(phi1) / R1) * phi;

        var lat = Math.floor(1000000 * phi / this.drad) / 1000000;
        var lng = D * (1 + D * D * ((-1 - 2 * T1 - C1) / 6 + D * D * (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * e0sq + 24 * T1 * T1) / 120)) / Math.cos(phi1);
        lng = lngd = zcm + lng / this.drad;

        return { lat: lat, lng: lng };
    },


   
}


utmconv.setDatum(0);    // Northern hemisphere
zone = 16               // for Madison, WI
var latlon = utmconv.utmToLatLng(easting, northing, zone, false);

console.log(latlon);





