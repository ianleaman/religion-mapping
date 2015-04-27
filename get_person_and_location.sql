SELECT lon, lat, birth_year, death_year, religion, party, subject
  FROM schema_location
  JOIN schema_person_places 
    ON schema_person_places.location_id = schema_location.id
  JOIN schema_person
    ON schema_person.id = schema_person_places.person_id