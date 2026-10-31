import axios from "axios";
import * as mock from "./mockData";

const USE_MOCK = true; // set to false when the backend is ready
const STUDENT_ID = 1;

const http = axios.create({ baseURL: "/api" });
const wait = (data, ms = 600) => new Promise((res) => setTimeout(() => res(data), ms));

export const getHealth = () =>
  USE_MOCK ? wait({ status: "ok", ai_mode: "fallback" }, 100) : http.get("/health").then((r) => r.data);

export const getQuestions = (params = {}) =>
  USE_MOCK ? wait(mock.mockQuestions) : http.get("/questions", { params }).then((r) => r.data);

export const submitDiagnostic = (answers) =>
  USE_MOCK
    ? wait(mock.mockDiagnosticResult, 1000)
    : http.post("/diagnostic/submit", { student_id: STUDENT_ID, answers }).then((r) => r.data);

export const evaluateAnswer = (question_id, answer_text) =>
  USE_MOCK
    ? wait(mock.mockEvaluation, 1500)
    : http.post("/evaluate-answer", { student_id: STUDENT_ID, question_id, answer_text }).then((r) => r.data);

export const getProgress = () =>
  USE_MOCK ? wait(mock.mockProgress) : http.get("/student/progress", { params: { student_id: STUDENT_ID } }).then((r) => r.data);

export const getMastery = () =>
  USE_MOCK ? wait(mock.mockMastery) : http.get("/student/mastery", { params: { student_id: STUDENT_ID } }).then((r) => r.data);

export const getRevisions = () =>
  USE_MOCK ? wait(mock.mockRevisions) : http.get("/student/revisions", { params: { student_id: STUDENT_ID } }).then((r) => r.data);

export const getTeacherAnalytics = () =>
  USE_MOCK ? wait(mock.mockTeacher) : http.get("/teacher/analytics").then((r) => r.data);