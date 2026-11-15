# questionnaire Skill Test Questions

Questions for an agent working with FHIR Questionnaires and SDC. Answer each in a few sentences, as you
would to a forms developer. Then do task TK-01. The answer key is in `answers.md`; don't read it.

Our content is FHIR R4 and follows SDC 4.0.0. "Our server" is HAPI FHIR with clinical-reasoning 4.13.0.

## Structure

**ST-01. Nesting.** Can a `boolean` question have child items, or must I wrap them in a group? Where do
the children's answers go in the QuestionnaireResponse?

**ST-02. Two conditions.** An item has two `enableWhen` entries and no `enableBehavior`, and our validator
doesn't complain. Is it valid?

**ST-03. A default choice.** I want one of an item's `answerOption`s selected by default. Can I put it in
`initial`?

**ST-04. R5.** We're moving these forms to R5 later. What happens to our `choice` and `open-choice` items?

## Expressions

**EX-01. A calculated field.** How do I make an item's answer a computed value that updates as the user
fills in the form? Is `cqf-calculatedValue` the right extension, and can the user override it?

**EX-02. Two libraries.** Our Questionnaire lists two CQL libraries with `cqf-library`, and both define
`"Given Name"`. How should an `initialExpression` name the one in `OtherLib`, per SDC, and what works on
our server?

**EX-03. %patient.** An `initialExpression` of `%patient.birthDate` (`text/fhirpath`) comes back empty on
our server, with an issue "Could not resolve identifier %patient". The Questionnaire declares a `patient`
launchContext. What's wrong?

**EX-04. Launch contexts.** Which `launchContext` codes does SDC 4.0.0 define?

## $populate

**PO-01. The request.** Write the `context` part of a `$populate` request that supplies the patient.
Is `name` a Coding?

**PO-02. The response.** Does `$populate` put pre-filled values in `initial` or `answer`?

**PO-03. Two answers.** An item that isn't repeating came back from our server with two answers. Why,
and how do I fix it?

**PO-04. A gender question.** A `choice` item with Coding answerOptions, pre-filled from `Patient.gender`
in CQL, comes back from our server as `valueString` `female`. Why, and what should the expression return?

**PO-05. Disabled items.** An item is disabled by its `enableWhen`, yet our server's `$populate` gave it an
answer. Is that what SDC expects?

**PO-06. An encounter.** We call `$populate` with `subject` and a `context` named `encounter`. The response
has no answers, no errors, and its subject is the Encounter. Why?

**PO-07. Observation-based population.** Will our server pre-fill an item that has a LOINC `code` and
`observationLinkPeriod`, but no expression?

## $extract

**XT-01. Unwanted Observations.** Our server's `$extract` creates Observations for coded items we never
marked with `observationExtract`. Why, and how do we stop it?

**XT-02. A failing extract.** `$extract` fails on a response with a `decimal` answer to a coded item.
What's happening?

**XT-03. definitionExtract.** We wrote SDC 4.0.0's `definitionExtract` (with a `definition`
sub-extension) on a group, and `$extract` throws "Unable to retrieve definition for item". What does our
server expect?

**XT-04. Saving.** Does `$extract` store the resources it creates?

## Versions

**VR-01. A newer server.** A server runs clinical-reasoning 4.15.0. How do we find out whether what the
skill says about `$populate` still holds?

## Task

**TK-01. A pre-visit intake form.** Write, in IG layout (`input/resources/`, `input/tests/`), an SDC
Questionnaire and a Library (CQL in its content) that conform to SDC 4.0.0 and that our server can
`$populate` and `$extract`, for:

- the patient's given name (string), pre-filled;
- the most recent body weight (quantity, LOINC 29463-7), pre-filled, and extracted as an Observation;
- "Do you smoke?" (boolean), and "Packs per day" (integer), shown only if they smoke;
- the patient's active conditions: a repeating group with one repetition per active Condition, each
  pre-filled with the condition's code.

Add a synthetic test patient with at least two weights and two conditions, and a completed
QuestionnaireResponse to extract. Use canonicals under `http://example.org/fhir`.
