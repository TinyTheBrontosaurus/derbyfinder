CREATE TABLE location
(
    locationId SERIAL PRIMARY KEY,
    -- Latitude in degrees
    lat REAL,
    -- Longitude in degrees
    lon REAL,
    address CHARACTER(255)
);

CREATE TABLE picture
(
    pictureId SERIAL PRIMARY KEY,
    -- The filename of the picture
    fileName CHARACTER(255),
    -- The latitude, in degrees
    lat REAL,
    -- The longitude, in degrees    
    lon REAL,
    -- The zoom factor
    zoom INTEGER
);

CREATE TABLE travelcost
(
    travelCostId SERIAL PRIMARY KEY,
    --Location of the origin
    originLocationId INTEGER REFERENCES location(locationId),
    --Location of the field/destination
    destLocationId INTEGER REFERENCES location(locationId),
    -- Time in seconds from origin to destination
    travelTime REAL,
    -- Distance in meters from origin to destination
    travelDist REAL
);

CREATE TABLE field
(
    fieldId SERIAL PRIMARY KEY,
    locationId INTEGER REFERENCES location(locationId),
    -- The heading of home plate to 2nd base		
    angle REAL,
    -- True if not a baseball field, false otherwise
    falsePositive BOOLEAN NOT NULL DEFAULT FALSE, 
    -- True if a good derby field, false if not, null if unknown
    good BOOLEAN,
    -- The approximate length of the field, in meters (assuming field is square)
    fieldSize REAL,
    -- The image on which the field was found
    pictureId INTEGER REFERENCES picture(pictureId),
    -- The ID of this field's duplicate. Null if not a duplicate. Null if this i the original
    duplicateId INTEGER REFERENCES field(fieldId)
);


