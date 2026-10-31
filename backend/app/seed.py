from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Concept, Question, Student

SEED_DATA = [
    {
        "concept": "Ohm's Law",
        "chapter": "Electricity",
        "questions": [
            {
                "text": "State Ohm's law and explain what it tells us about current and voltage.",
                "difficulty": "easy",
                "expected_answer": (
                    "At constant temperature, the current through a conductor is directly "
                    "proportional to the potential difference across its ends (V = IR). If the "
                    "voltage doubles, the current doubles, and the resistance stays constant."
                ),
                "key_concepts": [
                    "current proportional to potential difference",
                    "constant temperature",
                    "V = IR",
                    "resistance stays constant",
                ],
                "is_diagnostic": True,
            },
            {
                "text": (
                    "A wire has a resistance of 10 ohms. If the voltage across it is raised from "
                    "5 V to 10 V, what happens to the current and to the resistance, and why?"
                ),
                "difficulty": "medium",
                "expected_answer": (
                    "The current doubles (from 0.5 A to 1 A) because current is proportional to "
                    "voltage. The resistance stays at 10 ohms because it depends on the wire's "
                    "material, length, thickness and temperature, not on the applied voltage."
                ),
                "key_concepts": [
                    "current doubles",
                    "resistance unchanged",
                    "resistance depends on material, length, area, temperature",
                ],
                "is_diagnostic": False,
            },
        ],
    },
    {
        "concept": "Series and Parallel Circuits",
        "chapter": "Electricity",
        "questions": [
            {
                "text": "What is the difference between a series and a parallel circuit in terms of how current flows?",
                "difficulty": "easy",
                "expected_answer": (
                    "In a series circuit the components are connected end to end in a single "
                    "path, so the same current flows through all of them. In a parallel circuit "
                    "the components sit on separate branches across the same voltage, and the "
                    "current divides between the branches."
                ),
                "key_concepts": [
                    "series: single path, same current",
                    "parallel: separate branches",
                    "current divides in parallel",
                ],
                "is_diagnostic": True,
            },
            {
                "text": "Why are household appliances connected in parallel rather than in series?",
                "difficulty": "hard",
                "expected_answer": (
                    "In parallel, each appliance receives the full supply voltage and works "
                    "independently, so switching one off or a fault in one does not stop the "
                    "others. In series the voltage would be shared and breaking the circuit "
                    "anywhere would switch everything off."
                ),
                "key_concepts": [
                    "each appliance gets full voltage",
                    "appliances work independently",
                    "series would share voltage and one break stops all",
                ],
                "is_diagnostic": False,
            },
        ],
    },
    {
        "concept": "Electric Power and Heating Effect",
        "chapter": "Electricity",
        "questions": [
            {
                "text": "What is electric power and how is it calculated?",
                "difficulty": "easy",
                "expected_answer": (
                    "Electric power is the rate at which electrical energy is consumed or "
                    "converted into other forms. P = VI = I^2 R = V^2 / R, measured in watts."
                ),
                "key_concepts": [
                    "rate of energy consumption",
                    "P = VI",
                    "unit is watt",
                ],
                "is_diagnostic": True,
            },
            {
                "text": (
                    "Why does a bulb's filament become hot enough to glow while the copper wires "
                    "carrying current to it stay relatively cool?"
                ),
                "difficulty": "medium",
                "expected_answer": (
                    "Heat produced is H = I^2 R t. The same current flows through both, but the "
                    "filament is thin and has a very high resistance, so a lot of heat is produced "
                    "in it, while the thick, low-resistance copper wire produces very little."
                ),
                "key_concepts": [
                    "same current in both",
                    "filament has high resistance",
                    "heat = I^2 R t",
                    "copper wire has low resistance",
                ],
                "is_diagnostic": False,
            },
        ],
    },
    {
        "concept": "Refraction of Light",
        "chapter": "Light",
        "questions": [
            {
                "text": "What is refraction of light and why does it happen?",
                "difficulty": "easy",
                "expected_answer": (
                    "Refraction is the bending of light when it passes from one transparent "
                    "medium to another at an angle. It happens because the speed of light is "
                    "different in different media."
                ),
                "key_concepts": [
                    "bending of light at boundary",
                    "change of medium",
                    "speed of light differs in different media",
                ],
                "is_diagnostic": True,
            },
            {
                "text": "When light travels from air into glass, does it bend towards or away from the normal? Explain.",
                "difficulty": "medium",
                "expected_answer": (
                    "It bends towards the normal. Glass is optically denser than air, so light "
                    "slows down in glass, and light entering a denser medium bends towards the normal."
                ),
                "key_concepts": [
                    "bends towards the normal",
                    "glass is optically denser",
                    "light slows down in denser medium",
                ],
                "is_diagnostic": False,
            },
        ],
    },
    {
        "concept": "Image Formation by Lenses",
        "chapter": "Light",
        "questions": [
            {
                "text": (
                    "What kind of image does a convex lens form when an object is placed between "
                    "the lens and its focus?"
                ),
                "difficulty": "easy",
                "expected_answer": (
                    "A virtual, erect (upright) and magnified image on the same side of the lens "
                    "as the object. This is how a magnifying glass works."
                ),
                "key_concepts": [
                    "virtual image",
                    "erect image",
                    "magnified",
                    "same side as object",
                ],
                "is_diagnostic": True,
            },
            {
                "text": (
                    "How does the image formed by a convex lens change as an object moves from "
                    "far away towards the focus?"
                ),
                "difficulty": "hard",
                "expected_answer": (
                    "As the object comes closer, the real, inverted image moves farther from the "
                    "lens and gets larger. It is highly diminished at the focus for a very distant "
                    "object, the same size at 2F, and magnified when the object is between F and "
                    "2F. When the object reaches F the image goes to infinity."
                ),
                "key_concepts": [
                    "image is real and inverted",
                    "image moves away from lens",
                    "image gets larger",
                    "same size at 2F",
                    "image at infinity when object at F",
                ],
                "is_diagnostic": False,
            },
        ],
    },
    {
        "concept": "Magnetic Effect of Current",
        "chapter": "Magnetic Effects of Electric Current",
        "questions": [
            {
                "text": "What happens to a compass needle placed near a wire carrying electric current, and what does this show?",
                "difficulty": "easy",
                "expected_answer": (
                    "The needle is deflected, which shows that a current-carrying wire produces a "
                    "magnetic field around it (Oersted's experiment). Reversing the direction of "
                    "the current reverses the deflection."
                ),
                "key_concepts": [
                    "needle deflects",
                    "current produces magnetic field",
                    "reversing current reverses deflection",
                ],
                "is_diagnostic": True,
            },
            {
                "text": "How can you find the direction of the force on a current-carrying conductor placed in a magnetic field?",
                "difficulty": "medium",
                "expected_answer": (
                    "Use Fleming's left-hand rule. Stretch the thumb, forefinger and middle finger "
                    "of the left hand at right angles to each other: the forefinger points along "
                    "the magnetic field, the middle finger along the current, and the thumb shows "
                    "the direction of the force."
                ),
                "key_concepts": [
                    "Fleming's left-hand rule",
                    "forefinger = field",
                    "middle finger = current",
                    "thumb = force",
                ],
                "is_diagnostic": False,
            },
        ],
    },
]


def seed_database(db: Session) -> None:
    # The demo student (no login in the MVP)
    if db.get(Student, 1) is None:
        db.add(Student(id=1, name="Demo Student"))

    for item in SEED_DATA:
        concept = db.scalar(select(Concept).where(Concept.name == item["concept"]))
        if concept is None:
            concept = Concept(name=item["concept"], chapter=item["chapter"])
            db.add(concept)
            db.flush()  # sends the INSERT now so concept.id gets assigned

        for q in item["questions"]:
            already_there = db.scalar(select(Question).where(Question.text == q["text"]))
            if already_there is None:
                db.add(Question(concept_id=concept.id, **q))

    db.commit()