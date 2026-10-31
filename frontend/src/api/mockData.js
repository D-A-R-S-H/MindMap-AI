export const mockQuestions = [
  {
    id: 1,
    concept_id: 1,
    concept_name: "Reflection of light",
    question_text: "What is reflection of light?",
    difficulty: 1,
    expected_answer:
      "Reflection is the bouncing back of light when it strikes a smooth, polished surface.",
    key_concepts: ["bouncing back of light", "smooth/polished surface"],
  },
  {
    id: 2,
    concept_id: 2,
    concept_name: "Laws of reflection",
    question_text: "State the two laws of reflection of light.",
    difficulty: 1,
    expected_answer:
      "1) The angle of incidence equals the angle of reflection. 2) The incident ray, reflected ray and normal all lie in the same plane.",
    key_concepts: ["angle i = angle r", "same plane", "normal"],
  },
  {
    id: 3,
    concept_id: 4,
    concept_name: "Mirror formula",
    question_text: "Write the mirror formula and explain each term.",
    difficulty: 2,
    expected_answer:
      "1/v + 1/u = 1/f, where v is image distance, u is object distance and f is focal length.",
    key_concepts: ["1/v + 1/u = 1/f", "image distance", "object distance", "focal length"],
  },
];

export const mockEvaluation = {
  recall_score: 72,
  understanding_score: 65,
  answer_type: "partial",
  correct_points: ["Angle of incidence equals angle of reflection"],
  missing_points: ["Incident ray, reflected ray and normal lie in the same plane"],
  incorrect_points: [],
  misconceptions: ["Confused the normal with the reflecting surface"],
  improvement_suggestions: ["Explain what the normal is and draw a ray diagram."],
  follow_up_question: "Why is the angle measured from the normal and not the surface?",
  is_fallback: true,
  updated_mastery: { concept_id: 2, concept_name: "Laws of reflection", old: 45, new: 58 },
  next_question: { id: 3, question_text: "Write the mirror formula and explain each term.", concept_name: "Mirror formula" },
  next_revision_date: "2026-11-01",
};

export const mockDiagnosticResult = {
  profile: [
    { concept_id: 1, concept_name: "Reflection of light", mastery: 80, level: "strong" },
    { concept_id: 2, concept_name: "Laws of reflection", mastery: 45, level: "weak" },
    { concept_id: 4, concept_name: "Mirror formula", mastery: 60, level: "developing" },
  ],
  weak_concepts: ["Laws of reflection"],
  strong_concepts: ["Reflection of light"],
};

export const mockProgress = {
  name: "Swastika",
  overall_progress: 62,
  questions_attempted: 14,
  avg_recall: 68,
  avg_understanding: 61,
  strong_concepts: ["Reflection of light", "Refraction of light"],
  weak_concepts: ["Mirror formula", "Lens formula"],
  recent_activity: [
    { question: "State the laws of reflection", concept: "Laws of reflection", recall: 72, understanding: 65, at: "2026-10-31T10:30:00" },
  ],
};

export const mockMastery = [
  { concept_id: 1, concept_name: "Reflection of light", mastery: 80, attempts: 3, level: "strong" },
  { concept_id: 2, concept_name: "Laws of reflection", mastery: 45, attempts: 2, level: "weak" },
  { concept_id: 3, concept_name: "Spherical mirrors", mastery: 55, attempts: 2, level: "developing" },
  { concept_id: 4, concept_name: "Mirror formula", mastery: 38, attempts: 1, level: "weak" },
  { concept_id: 5, concept_name: "Refraction of light", mastery: 78, attempts: 3, level: "strong" },
  { concept_id: 6, concept_name: "Refractive index", mastery: 60, attempts: 2, level: "developing" },
  { concept_id: 7, concept_name: "Refraction through lenses", mastery: 50, attempts: 1, level: "developing" },
  { concept_id: 8, concept_name: "Lens formula", mastery: 35, attempts: 1, level: "weak" },
  { concept_id: 9, concept_name: "Power of a lens", mastery: 66, attempts: 2, level: "developing" },
];

export const mockRevisions = [
  { concept_id: 4, concept_name: "Mirror formula", due_date: "2026-11-01", priority: "high" },
  { concept_id: 8, concept_name: "Lens formula", due_date: "2026-11-01", priority: "high" },
  { concept_id: 6, concept_name: "Refractive index", due_date: "2026-11-03", priority: "medium" },
];

export const mockTeacher = {
  class_avg_mastery: 58,
  concepts: [
    { name: "Mirror formula", avg_mastery: 40 },
    { name: "Lens formula", avg_mastery: 42 },
    { name: "Reflection of light", avg_mastery: 82 },
  ],
  common_misconceptions: [
    { text: "Image in a plane mirror is real", count: 6 },
    { text: "Light bends because it slows only at the surface", count: 4 },
  ],
  students: [
    { name: "Aarav", avg_mastery: 72, weakest_concept: "Lens formula" },
    { name: "Meera", avg_mastery: 45, weakest_concept: "Mirror formula" },
  ],
  needs_teaching: ["Mirror formula", "Lens formula"],
};