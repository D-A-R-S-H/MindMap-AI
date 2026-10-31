"""Seed data: Class 10 Physics, Light: Reflection and Refraction.

Safe to run many times. If you change questions after the first run, delete
backend/mindmap.db and restart so the database is rebuilt.
"""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .mastery import get_level
from .models import Concept, Mastery, Misconception, Question, RevisionSchedule, Student
from .revision import schedule_revision

CHAPTER = "Light: Reflection and Refraction"

# (text, difficulty 1-3, expected_answer, key_concepts, is_diagnostic)
SEED_DATA = [
    ("Reflection of light", [
        ("What is reflection of light, and from what kind of surface does it give a clear image?", 1,
         "Reflection is the bouncing back of light into the same medium when it strikes a surface. "
         "Smooth, polished surfaces like mirrors give regular reflection and clear images, while rough "
         "surfaces scatter light in many directions.",
         ["bouncing back of light", "smooth polished surface gives clear image", "rough surface scatters light"], True),
        ("Why can you see your face in a mirror but not in a wall, even though both reflect light?", 2,
         "Both reflect light, but a mirror is smooth, so parallel rays stay parallel after reflection "
         "(regular reflection) and form an image. A wall is rough, so rays are reflected in many "
         "directions (diffuse reflection) and no image forms.",
         ["mirror smooth regular reflection", "wall rough diffuse reflection",
          "rays scattered in many directions", "no image forms on rough surface"], False),
    ]),
    ("Laws of reflection", [
        ("State the two laws of reflection of light.", 1,
         "1) The angle of incidence is equal to the angle of reflection. 2) The incident ray, the "
         "reflected ray and the normal at the point of incidence all lie in the same plane.",
         ["angle of incidence equals angle of reflection",
          "incident ray reflected ray and normal in same plane", "angles measured from the normal"], True),
        ("A ray strikes a plane mirror making 30 degrees with the mirror surface. What is the angle of "
         "reflection, and how do you work it out?", 2,
         "The angle between the ray and the surface is 30 degrees, so the angle of incidence, measured "
         "from the normal, is 90 - 30 = 60 degrees. By the law of reflection the angle of reflection "
         "is also 60 degrees.",
         ["angle of incidence is measured from the normal", "90 minus 30 gives 60 degrees",
          "angle of reflection equals 60 degrees"], False),
    ]),
    ("Spherical mirrors", [
        ("Differentiate between a concave and a convex mirror, and give one use of each.", 1,
         "A concave mirror curves inward, converges parallel rays to a focus and is used in torches, "
         "shaving mirrors and headlights. A convex mirror bulges outward, diverges parallel rays and is "
         "used as a rear-view mirror because it gives a wider field of view with an erect, smaller image.",
         ["concave mirror converges light", "convex mirror diverges light",
          "concave used in headlights or shaving mirror", "convex used as rear-view mirror with wider view"], True),
        ("Define the principal focus and focal length of a concave mirror. How is the focal length "
         "related to the radius of curvature?", 2,
         "The principal focus is the point on the principal axis where rays parallel to the axis meet "
         "after reflection. The focal length is the distance from the pole to the principal focus. "
         "The focal length is half the radius of curvature, f = R/2.",
         ["parallel rays meet at the principal focus", "focal length is distance from pole to focus",
          "focal length is half the radius of curvature"], False),
    ]),
    ("Mirror formula", [
        ("Write the mirror formula and explain what each symbol means.", 2,
         "The mirror formula is 1/v + 1/u = 1/f, where u is the object distance, v is the image "
         "distance and f is the focal length, all measured from the pole of the mirror using the sign "
         "convention.",
         ["1/v + 1/u = 1/f", "u is the object distance", "v is the image distance",
          "f is the focal length", "distances measured from the pole with sign convention"], True),
        ("An object is placed 30 cm in front of a concave mirror of focal length 15 cm. Where is the "
         "image formed and what is its nature?", 3,
         "With the sign convention u = -30 cm and f = -15 cm. 1/v = 1/f - 1/u = -1/15 + 1/30 = -1/30, "
         "so v = -30 cm. The image forms 30 cm in front of the mirror, at the centre of curvature, and "
         "is real, inverted and the same size as the object.",
         ["image is 30 cm in front of the mirror", "image formed at the centre of curvature",
          "image is real and inverted", "image is the same size as the object"], False),
    ]),
    ("Refraction of light", [
        ("What is refraction of light and why does it happen?", 1,
         "Refraction is the change in direction (bending) of light when it passes obliquely from one "
         "transparent medium to another. It happens because the speed of light is different in "
         "different media.",
         ["bending of light at the boundary of two media", "happens when light enters obliquely",
          "speed of light changes between media"], True),
        ("State the laws of refraction (Snell's law). What happens when light goes from air into glass?", 2,
         "1) The incident ray, the refracted ray and the normal lie in the same plane. 2) The ratio "
         "sin i / sin r is constant for a given pair of media (Snell's law). Going from air (rarer) to "
         "glass (denser), light slows down and bends towards the normal.",
         ["incident ray refracted ray and normal in same plane", "sin i by sin r is constant Snell's law",
          "from rarer to denser medium light bends towards the normal", "light slows down in glass"], False),
    ]),
    ("Refractive index", [
        ("Define refractive index and write its formula. What does a higher refractive index tell you?", 2,
         "The absolute refractive index of a medium is the ratio of the speed of light in vacuum to "
         "the speed of light in that medium: n = c / v. A higher refractive index means light travels "
         "slower in it and the medium is optically denser, so light bends more towards the normal.",
         ["ratio of speed of light in vacuum to speed in the medium", "n = c / v",
          "higher refractive index means light travels slower", "optically denser medium bends light more"], True),
        ("The refractive index of glass is 1.5 and the speed of light in vacuum is 3 x 10^8 m/s. Find "
         "the speed of light in glass and show your steps.", 2,
         "n = c / v, so v = c / n = (3 x 10^8) / 1.5 = 2 x 10^8 m/s. Light is slower in glass than in "
         "vacuum.",
         ["speed in medium equals c divided by n", "speed of light in glass is 2 x 10^8 metres per second",
          "light is slower in glass than in vacuum"], False),
    ]),
    ("Refraction through lenses", [
        ("How does a convex lens differ from a concave lens in the way it bends light?", 1,
         "A convex lens is thicker at the centre and converges parallel rays to the principal focus, so "
         "it is a converging lens. A concave lens is thinner at the centre and diverges parallel rays "
         "so they appear to come from its principal focus, so it is a diverging lens.",
         ["convex lens converges light", "concave lens diverges light",
          "convex lens is thicker at the centre", "concave lens is thinner at the centre"], True),
        ("Describe the three rays you would use to locate the image formed by a convex lens.", 2,
         "(1) A ray parallel to the principal axis passes through the principal focus after refraction. "
         "(2) A ray through the optical centre goes straight without deviation. (3) A ray through the "
         "principal focus becomes parallel to the principal axis after refraction.",
         ["parallel ray passes through the principal focus", "ray through optical centre goes undeviated",
          "ray through the focus emerges parallel to the axis"], False),
    ]),
    ("Lens formula", [
        ("Write the lens formula and the magnification formula. What do the symbols mean?", 2,
         "The lens formula is 1/v - 1/u = 1/f, where u is the object distance, v the image distance and "
         "f the focal length, measured from the optical centre. Magnification m = h'/h = v/u, the ratio "
         "of image height to object height. A negative m means a real, inverted image.",
         ["1/v - 1/u = 1/f", "u is object distance v is image distance f is focal length",
          "magnification equals v by u", "magnification is ratio of image height to object height"], True),
        ("An object is placed 20 cm from a convex lens of focal length 10 cm. Find the image distance "
         "and describe the image.", 3,
         "u = -20 cm and f = +10 cm. 1/v = 1/f + 1/u = 1/10 - 1/20 = 1/20, so v = +20 cm. The "
         "magnification m = v/u = -1, so the image is real, inverted and the same size, formed 20 cm on "
         "the other side of the lens.",
         ["image distance is 20 cm on the other side of the lens", "magnification is minus one",
          "image is real and inverted", "image is the same size as the object"], True),
    ]),
    ("Power of a lens", [
        ("What is the power of a lens? State its formula and unit.", 1,
         "The power of a lens is the reciprocal of its focal length in metres: P = 1/f. Its SI unit is "
         "the dioptre (D). A convex lens has positive power and a concave lens has negative power.",
         ["power is the reciprocal of focal length", "P = 1/f with f in metres", "unit is the dioptre",
          "convex lens positive power concave lens negative power"], True),
        ("A doctor prescribes a lens of power -2.5 D. What kind of lens is it and what is its focal length?", 2,
         "Negative power means a concave (diverging) lens. f = 1/P = 1/(-2.5) = -0.4 m, that is -40 cm.",
         ["negative power means a concave lens", "focal length equals 1 divided by power",
          "focal length is minus 0.4 metres or minus 40 cm"], False),
    ]),
]

# ---- sample class (for the teacher dashboard) ----
CONCEPT_BASE = {
    "Reflection of light": 82, "Laws of reflection": 70, "Spherical mirrors": 62,
    "Mirror formula": 40, "Refraction of light": 74, "Refractive index": 58,
    "Refraction through lenses": 55, "Lens formula": 38, "Power of a lens": 60,
}
CLASS_STUDENTS = [("Aarav", 12), ("Meera", -10), ("Rohan", 2), ("Ananya", 8),
                  ("Kabir", -14), ("Isha", 4), ("Vihaan", -4), ("Diya", 15)]
MISCONCEPTION_BY_CONCEPT = {
    "Reflection of light": "Image in a plane mirror is real",
    "Laws of reflection": "Angle of reflection is measured from the mirror surface, not the normal",
    "Spherical mirrors": "Convex mirrors converge light",
    "Mirror formula": "All distances in the mirror formula are positive",
    "Refraction of light": "Light bends because the glass absorbs it",
    "Refractive index": "Refractive index depends on the angle of incidence",
    "Refraction through lenses": "A convex lens always forms a magnified image",
    "Lens formula": "A concave lens always forms a real image",
    "Power of a lens": "A lens with a longer focal length has more power",
}


def _seed_class(db: Session, concepts: dict[str, Concept]) -> None:
    if (db.scalar(select(func.count()).select_from(Student)) or 0) >= 2:
        return
    today = date.today()
    for sid, (name, offset) in enumerate(CLASS_STUDENTS, start=2):
        student = Student(name=name)
        db.add(student)
        db.flush()
        scored = []
        for concept in concepts.values():
            jitter = ((concept.id * 7 + sid * 13) % 15) - 7
            score = float(max(5, min(98, CONCEPT_BASE[concept.name] + offset + jitter)))
            db.add(Mastery(student_id=student.id, concept_id=concept.id, score=score, attempt_count=2))
            due, priority = schedule_revision(get_level(score), today)
            db.add(RevisionSchedule(student_id=student.id, concept_id=concept.id, due_date=due, priority=priority))
            scored.append((score, concept))
        weakest = [c for _, c in sorted(scored, key=lambda x: x[0])[:4]]  # four weakest concepts
        picks = {weakest[sid % 4], weakest[(sid * 3 + 1) % 4]}            # varies per student
        for concept in picks:
            db.add(Misconception(student_id=student.id, concept_id=concept.id, attempt_id=None,
                                 description=MISCONCEPTION_BY_CONCEPT[concept.name]))


def seed_database(db: Session) -> None:
    if db.get(Student, 1) is None:
        db.add(Student(id=1, name="Demo Student"))

    concepts: dict[str, Concept] = {}
    for name, questions in SEED_DATA:
        concept = db.scalar(select(Concept).where(Concept.name == name))
        if concept is None:
            concept = Concept(name=name, chapter=CHAPTER)
            db.add(concept)
            db.flush()
        concepts[name] = concept
        for text, difficulty, expected, keys, is_diag in questions:
            if db.scalar(select(Question).where(Question.text == text)) is None:
                db.add(Question(concept_id=concept.id, text=text, difficulty=difficulty,
                                expected_answer=expected, key_concepts=keys, is_diagnostic=is_diag))
    db.flush()
    _seed_class(db, concepts)
    db.commit()
