# Jackson-Hibernate-Annotation-Migrator
Script to switch Jackson annotations to field getters/setters for Java Hibernate entities

### Introduction
  * Having `JacksonAnnotations` preceding variable declarations assists with readability when creating an entity
  * Having them precede variable getter/setter definitions allows us to annotate a getter and setter differently
  * The EAM automatically migrates `JacksonAnnotations` from variable declarations to variable getters/setters!
  * Verified functional for Hibernate annotations v4.3.x

Featuring Python's powerful string-parsing capabilities, the EAM does the following:
  * Switches positions of `JacksonAnnotations` and `HibernateAnnotations`
  * If `@JsonIgnore` in Getter, add `@JsonDeserialize` to Setter

### Usage
  * Run manually for each entity you want to switch the annotations for.
  * Change global variable `FILENAME` to the Entity file (`.java`) you want to migrate
  * Then execute e.g.
      `python3 EntityAnnotationMigrator.py > output.txt`
  * Fix any import statement issues in the output, and you're done!

### Future improvements
  * Keep functions like `equals()` and `hashCode()` where they're at, instead of printing them at the end
  	* Possible implementations: append to previous setter? use (ind, varName) keys for `variableInfo`?
  * Automatically detect partial migrations (currently, only deals with completed unmigrated entity files)
  * Advanced: Automatically generate JSON annotations based on variable/field!
