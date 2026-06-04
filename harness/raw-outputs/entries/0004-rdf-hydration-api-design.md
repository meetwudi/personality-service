# 0004: RDF Hydration API Design

## Topic

Knowledge graph hydration API

## Source

Human design discussion.

## Raw Discussion

The project is an experiment to hydrate a knowledge graph using AI. ChatGPT may be the first client, but the server should not be ChatGPT-specific and should work for other AI clients.

The ontology, or TBox, defines what the graph wants to know. The AI hydrates the graph through back-and-forth interaction with the graph by reading the TBox itself and querying the existing graph data, or ABox.

## Decisions

- Use an RDF and SPARQL based approach.
- A minimal implementation can use RDFLib.
- The graph can be stored in memory for the first version.
- `hydrate` means directly writing learned facts to the graph.
- The AI can read the ontology as raw text.
- Start API design with only two core endpoints:
  - `interrogate/`: examines the ontology and current graph data, then returns useful questions the graph wants answered in order to incrementally hydrate itself.
  - `learn/`: takes questions and answers, then ingests the answers back into the graph.
- `interrogate/` should return up to three questions by default, with the limit configurable.

## Open Questions Tabled For Later

- How does the graph know it already knows everything, or at least know that no useful hydration questions remain?
- Should `interrogate/` persist state and return stable `question_id` values?
- How should `learn/` handle clients mutating the questions before sending answers back?
- How should the service be deployed so ChatGPT can send requests to it, possibly using a minimal Google Cloud Platform instance?
- Technical implementation questions, including graph backend details beyond the RDFLib in-memory starting point, should be asked later rather than resolved during this initial design pass.

## Provided Ontology

```turtle
@prefix self: <https://example.org/self-graph#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

self:SelfGraphOntology a owl:Ontology .

### Core classes

self:Person a owl:Class .
self:Reflection a owl:Class .
self:Claim a owl:Class .
self:Evidence a owl:Class .
self:LifeDomain a owl:Class .
self:State a owl:Class .
self:Trait a owl:Class .
self:Value a owl:Class .
self:Need a owl:Class .
self:Preference a owl:Class .
self:Pattern a owl:Class .
self:Tension a owl:Class .
self:Trigger a owl:Class .
self:RestorativePractice a owl:Class .
self:Relationship a owl:Class .
self:Event a owl:Class .
self:Goal a owl:Class .
self:Boundary a owl:Class .
self:IdentityNarrative a owl:Class .

### Psychological-ish classes

self:EmotionalState rdfs:subClassOf self:State .
self:CognitiveState rdfs:subClassOf self:State .
self:SomaticState rdfs:subClassOf self:State .
self:MotivationalState rdfs:subClassOf self:State .

self:AutonomyNeed rdfs:subClassOf self:Need .
self:CompetenceNeed rdfs:subClassOf self:Need .
self:RelatednessNeed rdfs:subClassOf self:Need .

self:RecurringPattern rdfs:subClassOf self:Pattern .
self:AvoidanceLoop rdfs:subClassOf self:RecurringPattern .
self:GrowthEdge rdfs:subClassOf self:Pattern .

### Object properties

self:hasTrait a owl:ObjectProperty ;
  rdfs:domain self:Person ;
  rdfs:range self:Trait .

self:hasValue a owl:ObjectProperty ;
  rdfs:domain self:Person ;
  rdfs:range self:Value .

self:hasNeed a owl:ObjectProperty ;
  rdfs:domain self:Person ;
  rdfs:range self:Need .

self:hasCurrentState a owl:ObjectProperty ;
  rdfs:domain self:Person ;
  rdfs:range self:State .

self:hasPreference a owl:ObjectProperty ;
  rdfs:domain self:Person ;
  rdfs:range self:Preference .

self:hasPattern a owl:ObjectProperty ;
  rdfs:domain self:Person ;
  rdfs:range self:Pattern .

self:inDomain a owl:ObjectProperty ;
  rdfs:range self:LifeDomain .

self:hasEvidence a owl:ObjectProperty ;
  rdfs:domain self:Claim ;
  rdfs:range self:Evidence .

self:derivedFromReflection a owl:ObjectProperty ;
  rdfs:domain self:Claim ;
  rdfs:range self:Reflection .

self:expressesValue a owl:ObjectProperty ;
  rdfs:domain self:Claim ;
  rdfs:range self:Value .

self:thwartsNeed a owl:ObjectProperty ;
  rdfs:range self:Need .

self:satisfiesNeed a owl:ObjectProperty ;
  rdfs:range self:Need .

self:triggers a owl:ObjectProperty ;
  rdfs:domain self:Trigger ;
  rdfs:range self:State .

self:restores a owl:ObjectProperty ;
  rdfs:domain self:RestorativePractice ;
  rdfs:range self:State .

self:conflictsWith a owl:ObjectProperty, owl:SymmetricProperty .
self:supports a owl:ObjectProperty .
self:protectsAgainst a owl:ObjectProperty .
self:recursWith a owl:ObjectProperty .
self:changedAfter a owl:ObjectProperty .

### Data properties

self:claimText a owl:DatatypeProperty ;
  rdfs:domain self:Claim ;
  rdfs:range xsd:string .

self:confidence a owl:DatatypeProperty ;
  rdfs:domain self:Claim ;
  rdfs:range xsd:decimal .

self:createdAt a owl:DatatypeProperty ;
  rdfs:range xsd:dateTime .

self:lastObservedAt a owl:DatatypeProperty ;
  rdfs:range xsd:dateTime .

self:expiresAt a owl:DatatypeProperty ;
  rdfs:range xsd:dateTime .

self:evidenceText a owl:DatatypeProperty ;
  rdfs:domain self:Evidence ;
  rdfs:range xsd:string .

self:sourceType a owl:DatatypeProperty ;
  rdfs:range xsd:string .

self:privacyLevel a owl:DatatypeProperty ;
  rdfs:range xsd:string .

self:userApproved a owl:DatatypeProperty ;
  rdfs:domain self:Claim ;
  rdfs:range xsd:boolean .
```
