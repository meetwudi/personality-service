from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .ontology import RAW_ONTOLOGY

SELF = Namespace("https://example.org/self-graph#")
RUN = Namespace("https://example.org/self-graph/run/")


@dataclass
class GraphRecord:
    identifier: UUID
    graph: Graph
    asked_questions: set[str] = field(default_factory=set)
    learned_count: int = 0


class GraphStore:
    def __init__(self) -> None:
        self._records: dict[UUID, GraphRecord] = {}

    def get(self, identifier: UUID) -> GraphRecord:
        if identifier not in self._records:
            graph = Graph()
            graph.bind("self", SELF)
            graph.bind("run", RUN)
            graph.parse(data=RAW_ONTOLOGY, format="turtle")
            person = self.person_uri(identifier)
            graph.add((person, RDF.type, SELF.Person))
            graph.add((person, SELF.createdAt, self.now_literal()))
            self._records[identifier] = GraphRecord(identifier=identifier, graph=graph)
        return self._records[identifier]

    def mark_asked(self, record: GraphRecord, question: str, focus: str) -> None:
        normalized = normalize_question(question)
        if normalized in record.asked_questions:
            return

        record.asked_questions.add(normalized)
        asked = RUN[f"{record.identifier}/question/{uuid4()}"]
        record.graph.add((asked, RDF.type, SELF.Question))
        record.graph.add((asked, SELF.questionText, Literal(question)))
        record.graph.add((asked, SELF.questionFocus, Literal(focus)))
        record.graph.add((asked, SELF.createdAt, self.now_literal()))

    def learn(self, record: GraphRecord, question: str, answer: str) -> None:
        self.mark_asked(record, question, "learned-answer")
        created_at = self.now_literal()
        reflection = RUN[f"{record.identifier}/reflection/{uuid4()}"]
        evidence = RUN[f"{record.identifier}/evidence/{uuid4()}"]
        claim = RUN[f"{record.identifier}/claim/{uuid4()}"]

        record.graph.add((reflection, RDF.type, SELF.Reflection))
        record.graph.add((reflection, SELF.createdAt, created_at))
        record.graph.add((reflection, SELF.sourceType, Literal("learn_api")))
        record.graph.add((reflection, SELF.privacyLevel, Literal("experimental")))

        record.graph.add((evidence, RDF.type, SELF.Evidence))
        record.graph.add((evidence, SELF.evidenceText, Literal(f"Question: {question}\nAnswer: {answer}")))
        record.graph.add((evidence, SELF.sourceType, Literal("learn_api")))
        record.graph.add((evidence, SELF.createdAt, created_at))

        record.graph.add((claim, RDF.type, SELF.Claim))
        record.graph.add((claim, SELF.claimText, Literal(answer)))
        record.graph.add((claim, SELF.confidence, Literal(Decimal("0.50"))))
        record.graph.add((claim, SELF.userApproved, Literal(True, datatype=XSD.boolean)))
        record.graph.add((claim, SELF.createdAt, created_at))
        record.graph.add((claim, SELF.derivedFromReflection, reflection))
        record.graph.add((claim, SELF.hasEvidence, evidence))

        record.learned_count += 1

    def export_turtle(self, identifier: UUID) -> str:
        record = self.get(identifier)
        return record.graph.serialize(format="turtle")

    def graph_summary(self, record: GraphRecord) -> str:
        focus_counts = [
            ("Trait", SELF.Trait),
            ("Value", SELF.Value),
            ("Need", SELF.Need),
            ("State", SELF.State),
            ("Preference", SELF.Preference),
            ("Pattern", SELF.Pattern),
            ("Trigger", SELF.Trigger),
            ("RestorativePractice", SELF.RestorativePractice),
            ("Goal", SELF.Goal),
            ("Boundary", SELF.Boundary),
            ("IdentityNarrative", SELF.IdentityNarrative),
            ("Claim", SELF.Claim),
        ]
        lines = [f"learned_count: {record.learned_count}"]
        for label, rdf_class in focus_counts:
            lines.append(f"{label}: {self.count_instances(record, rdf_class)}")

        asked = sorted(record.asked_questions)
        if asked:
            lines.append("asked_questions:")
            lines.extend(f"- {question}" for question in asked[-25:])
        else:
            lines.append("asked_questions: none")

        claims = self.recent_claims(record)
        if claims:
            lines.append("recent_claims:")
            lines.extend(f"- {claim}" for claim in claims)
        else:
            lines.append("recent_claims: none")
        return "\n".join(lines)

    @staticmethod
    def count_instances(record: GraphRecord, rdf_class: URIRef) -> int:
        query = """
        SELECT (COUNT(?subject) AS ?count)
        WHERE {
          ?subject a ?class .
        }
        """
        result = record.graph.query(query, initBindings={"class": rdf_class})
        for row in result:
            return int(row[0])
        return 0

    @staticmethod
    def recent_claims(record: GraphRecord) -> list[str]:
        query = """
        SELECT ?text
        WHERE {
          ?claim a ?claimClass ;
            ?claimText ?text .
        }
        LIMIT 10
        """
        result = record.graph.query(
            query,
            initBindings={
                "claimClass": SELF.Claim,
                "claimText": SELF.claimText,
            },
        )
        return [str(row.text) for row in result]

    @staticmethod
    def person_uri(identifier: UUID) -> URIRef:
        return RUN[f"{identifier}/person/self"]

    @staticmethod
    def now_literal() -> Literal:
        return Literal(datetime.now(UTC).isoformat(), datatype=XSD.dateTime)


def parse_identifier(raw_identifier: str) -> UUID:
    try:
        identifier = UUID(raw_identifier)
    except ValueError as exc:
        raise ValueError("identifier must be a valid UUID") from exc
    if str(identifier) != raw_identifier.lower():
        raise ValueError("identifier must be a canonical UUID string")
    return identifier


def normalize_question(question: str) -> str:
    return " ".join(question.strip().lower().split())
