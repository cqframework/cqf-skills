Alias: $LNC = http://loinc.org
Alias: $UCUM = http://unitsofmeasure.org

CodeSystem: BPMethodCS
Id: bp-method
Title: "Blood Pressure Method"
* ^caseSensitive = true
* #auto "Automated cuff"
* #manual "Manual auscultation"

ValueSet: BPMethodVS
Id: bp-method
Title: "Blood Pressure Method"
* include codes from system BPMethodCS

Extension: ReviewedBy
Id: reviewed-by
Title: "Reviewed By"
Description: "The practitioner who reviewed the reading."
Context: Observation
* value[x] only Reference(Practitioner)

Profile: SimpleBP
Parent: Observation
Id: simple-bp
Title: "Simple Blood Pressure"
Description: "A blood pressure reading with systolic and diastolic components."
* status = #final
* code = $LNC#85354-9
* subject 1..1
* subject only Reference(Patient)
* method 1..1
* method from BPMethodVS (required)
* extension contains ReviewedBy named reviewedBy 0..1 MS
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains systolic 1..1 and diastolic 1..1
* component[systolic].code = $LNC#8480-6
* component[systolic].value[x] only Quantity
* component[systolic].valueQuantity = $UCUM#mm[Hg]
* component[diastolic].code = $LNC#8462-4
* component[diastolic].value[x] only Quantity
* component[diastolic].valueQuantity = $UCUM#mm[Hg]

Instance: example-bp
InstanceOf: SimpleBP
Usage: #example
* subject = Reference(Patient/example)
* method = BPMethodCS#auto
* extension[reviewedBy].valueReference = Reference(Practitioner/example)
* component[systolic].valueQuantity = 120 'mm[Hg]'
* component[diastolic].valueQuantity = 80 'mm[Hg]'
